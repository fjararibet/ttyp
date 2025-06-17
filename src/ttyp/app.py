from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from prompt_toolkit.document import Document
from prompt_toolkit.application.current import get_app_or_none
import textwrap
from itertools import zip_longest
from .ttyp import Ttyp


class TtypLexer(Lexer):
    def __init__(self, to_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.to_type = to_type
        self.width = None

    def lex_document(self, document: Document):

        def get_line(lineno):
            app = get_app_or_none()
            if app:
                window = app.layout.current_window
                if window and window.render_info:
                    self.width = window.render_info.window_width
            if not self.width:
                return []
            line = document.lines[lineno]
            tokens = []
            wrapped_to_type = textwrap.wrap(self.to_type, width=self.width)
            wrapped_lines = textwrap.wrap(self.to_type, width=self.width)
            for wrapped_line, wrapped_line_to_type in zip(wrapped_lines, wrapped_to_type):
                # here it needs to be word by word instead of char by char
                # to account for extra letters the user might have typed
                # in a word.
                for typed_word, word_to_type in zip(wrapped_line.split(), wrapped_line_to_type.split()):
                    # char by char
                    min_len = min(len(typed_word), len(word_to_type))
                    for i, j in zip(typed_word, word_to_type):
                        style = "typed" if i == j else "wrong"
                        tokens.append((f"class:{style}", j))

                    # leftover typed word
                    for c in typed_word[min_len:]:
                        style = "wrong"
                        tokens.append((f"class:{style}", c))

                    # leftover target word
                    for c in word_to_type[min_len:]:
                        style = "ghost"
                        tokens.append((f"class:{style}", c))

                    tokens.append(("", " "))

                # words left to type
                typed_wcount = len(wrapped_line)
                for i, word in enumerate(wrapped_line_to_type.split()[typed_wcount:]):
                    tokens.append(("class:ghost", word))
                    tokens.append(("", " "))
                tokens.append(("", " " * (self.width - len(wrapped_line_to_type)-1)))

            return tokens

        return get_line


class TtypBuffer(Buffer):
    def __init__(self, ttyp: Ttyp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ttyp = ttyp


class TtypApp():
    def __init__(self, ttyp: Ttyp, to_type: [str], erase_when_done: bool, debug: bool = False):
        self._to_type = to_type
        buffer = TtypBuffer(
            ttyp=ttyp,
            on_text_changed=self._on_change,
            on_text_insert=self._on_insert,
            on_cursor_position_changed=self._on_cursor_change
        )
        self._debug_buffer = Buffer()
        lexer = TtypLexer(to_type=to_type)
        root_container = HSplit([
            Window(BufferControl(buffer=buffer, lexer=lexer), wrap_lines=True),
        ])
        if debug:
            root_container = HSplit([
                Window(BufferControl(buffer=buffer, lexer=lexer), wrap_lines=True),
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

    # the following functions are defined in the order they
    # are ran on text insert

    def _on_change(self, buffer: TtypBuffer):
        ttyp = buffer.ttyp

        ttyp.set_cursor_position(buffer.cursor_position)
        ttyp.set_typed(buffer.text)
        # set_typed has side effects so the state
        # has to be updated
        new_cursor_position = ttyp.get_cursor_position()
        buffer.text = ttyp.get_typed()
        buffer.cursor_position = new_cursor_position

    def _on_cursor_change(self, buffer: TtypBuffer):
        ttyp = buffer.ttyp
        target = ttyp.get_cursor_position()
        if buffer.cursor_position != target:
            buffer.cursor_position = target

    def _on_insert(self, buffer: TtypBuffer):
        ttyp = buffer.ttyp
        cursor_position = buffer.cursor_position
        ttyp.insert_char()
        new_cursor_position = ttyp.get_cursor_position()

        # cursor can't be moved if the buffer is not big enough,
        # so spaces are added
        diff = new_cursor_position - cursor_position
        buffer.text += " " * diff

        # reset becasuse on_change was triggered with old value
        ttyp.set_cursor_position(new_cursor_position)
        buffer.cursor_position = new_cursor_position

        if ttyp.is_done():
            wpm = ttyp.get_wpm()
            acc = ttyp.get_acc()
            correct = ttyp.get_correct()
            mistakes = ttyp.get_mistakes()
            self._app.exit(
                result={
                    "wpm": wpm,
                    "acc": acc,
                    "correct": correct,
                    "mistakes": mistakes,
                })

    def _debug(self, text: str):
        self._debug_buffer.text += str(text) + " "
