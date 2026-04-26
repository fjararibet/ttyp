from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, UIContent
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from prompt_toolkit.document import Document
from prompt_toolkit.application import get_app
import textwrap
from .ttyp import Ttyp

class GhostBufferControl(BufferControl):
    def __init__(self, *args, to_type: list[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.to_type = to_type

    def create_content(self, width, height, preview_search=False):
        real = super().create_content(width, height, preview_search)

        wrapped = textwrap.wrap(
            " ".join(self.to_type),
            width=max(1, width - 1),
            break_long_words=False,
            break_on_hyphens=False,
        )

        typed_lines = self.buffer.document.lines  # always at least [""]
        total = max(len(typed_lines), len(wrapped))

        def render_line(typed_line: str, target_line: str):
            tokens = []
            typed_words = typed_line.split(" ") if typed_line else []
            target_words = target_line.split(" ")

            for idx, target_word in enumerate(target_words):
                if idx < len(typed_words):
                    typed_word = typed_words[idx]
                    # char-by-char comparison up to the shorter length
                    n = min(len(typed_word), len(target_word))
                    for i in range(n):
                        style = "class:typed" if typed_word[i] == target_word[i] else "class:wrong"
                        tokens.append((style, target_word[i]))
                    # extra chars the user typed beyond the target word
                    if len(typed_word) > n:
                        tokens.append(("class:wrong", typed_word[n:]))
                    # remaining chars of the target word still to type
                    if len(target_word) > n:
                        tokens.append(("class:ghost", target_word[n:]))
                else:
                    # whole word still to type
                    tokens.append(("class:ghost", target_word))

                # space between words (not after the last one)
                if idx < len(target_words) - 1:
                    tokens.append(("", " "))
            return tokens

        def get_line(lineno):
            typed_line = typed_lines[lineno] if lineno < len(typed_lines) else ""
            target_line = wrapped[lineno] if lineno < len(wrapped) else ""

            if not target_line:
                # past the ghost — defer to whatever the real BufferControl produced
                if lineno < real.line_count:
                    return real.get_line(lineno)
                return []

            return render_line(typed_line, target_line)

        return UIContent(
            get_line=get_line,
            line_count=total,
            cursor_position=real.cursor_position,
            show_cursor=real.show_cursor,
        )


class TtypBuffer(Buffer):
    def __init__(self, ttyp: Ttyp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ttyp = ttyp


class TtypApp():
    def __init__(self, ttyp: Ttyp, to_type: list[str], erase_when_done: bool, debug: bool = False):
        self._to_type = to_type
        buffer = TtypBuffer(
            ttyp=ttyp,
            on_text_insert=self._on_insert,
            on_cursor_position_changed=self._on_cursor_change
        )
        self._debug_buffer = Buffer()
        root_container = HSplit([
            Window(GhostBufferControl(to_type=to_type, buffer=buffer), wrap_lines=False),
        ])
        if debug:
            root_container = HSplit([
                Window(BufferControl(buffer=buffer), wrap_lines=True),
                Window(BufferControl(buffer=self._debug_buffer), wrap_lines=True)
            ])
        layout = Layout(root_container)

        style = Style.from_dict({
            "ghost": "#999999",
            "wrong": "#cc0000",
            "typed": "",
        })
        self._app = Application(
            layout=layout,
            key_bindings=self._create_keybindins(),
            full_screen=False,
            style=style,
            erase_when_done=erase_when_done,
        )

    def run(self):
        return self._app.run()

    def _create_keybindins(self):
        kb = KeyBindings()

        @kb.add('c-d')
        @kb.add('c-c')
        def exit_(event: KeyPressEvent):
            event.app.exit()

        @kb.add('enter')
        def disable_enter(event: KeyPressEvent):
            pass

        return kb

    def _on_cursor_change(self, buffer: TtypBuffer):
        end = len(buffer.text)
        if buffer.cursor_position < end:
            buffer.cursor_position = end

    def _on_insert(self, buffer: TtypBuffer):
        ttyp: Ttyp = buffer.ttyp
        new_cursor_position = ttyp.insert_char(
            typed=buffer.text,
            last_char=buffer.document.char_before_cursor,
            cursor_position=buffer.cursor_position,
        )
        # In case a space key is blocked
        if new_cursor_position == buffer.cursor_position - 1:
            buffer.text = buffer.text[:-1]

        # # cursor can't be moved ahead if the buffer is not big enough,
        # # so spaces are added
        diff = new_cursor_position - buffer.cursor_position
        buffer.text += " " * diff

        buffer.cursor_position = new_cursor_position

        if ttyp.is_done(buffer.text, buffer.cursor_position):
            wpm = ttyp.get_wpm(buffer.text)
            acc = ttyp.get_acc(buffer.text)
            correct = ttyp.get_correct(buffer.text)
            mistakes = ttyp.get_mistakes()
            self._app.exit(
                result={
                    "wpm": wpm,
                    "acc": acc,
                    "correct": correct,
                    "mistakes": mistakes,
                })

    def _debug(self, text):
        self._debug_buffer.text += str(text) + " "
