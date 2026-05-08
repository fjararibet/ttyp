from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, UIContent
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from prompt_toolkit.document import Document
from prompt_toolkit.application import get_app
from dataclasses import dataclass
import sys
import textwrap
from .ttyp import Ttyp


@dataclass
class VirtualLine:
    words: list[str]
    width: int

def ttyp_wrap(typed_words: list[str], to_type: list[str], width: int) -> list[str]:
    lines = []
    word_idx = 0
    while word_idx < len(typed_words):
        curr_line = VirtualLine(words=[], width=0)
        for type_word, to_type_word in zip(typed_words[word_idx:], to_type[word_idx:]):
            word_len = max(len(type_word), len(to_type_word)) + 1
            if curr_line.width + word_len > width:
                break
            curr_line.width += word_len
            curr_line.words.append(to_type_word)
        word_idx += len(curr_line.words)
        lines.append(curr_line)

    # remaining typing line
    if lines:
        i = 0
        for word in to_type[word_idx:]:
            word_len = len(word) + 1
            if lines and lines[-1].width + word_len > width:
                break
            lines[-1].width += word_len
            lines[-1].words.append(word)
            i += 1
        word_idx += i

    while word_idx < len(to_type):
        curr_line = VirtualLine(words=[], width=0)
        for to_type_word in to_type[word_idx:]:
            word_len = len(to_type_word) + 1
            if curr_line.width + word_len > width:
                break
            curr_line.width += word_len
            curr_line.words.append(to_type_word)
        word_idx += len(curr_line.words)
        lines.append(curr_line)
    str_line =  [
        " ".join(line.words) + " "
        for line in lines
    ]
    return str_line

class TtypBufferControl(BufferControl):
    def __init__(self, *args, to_type: list[str], **kwargs):
        super().__init__(*args, **kwargs)
        self._to_type = to_type
        self.wrapped = []

    def create_content(self, width, height, preview_search=False):
        real = super().create_content(width, height, preview_search)

        self.wrapped = ttyp_wrap(
            typed_words=self.buffer.text.split(),
            to_type=self._to_type,
            width=width,
        )

        typed_lines = self.buffer.document.lines  # always at least [""]
        def render_line(typed_line: str, target_line: str):
            tokens = []
            typed_words = typed_line.split(" ")
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

                # space between words
                if idx < len(target_words):
                    tokens.append(("", " "))
            return tokens

        def get_line(lineno):
            typed_line = typed_lines[lineno] if lineno < len(typed_lines) else ""
            target_line = self.wrapped[lineno] if lineno < len(self.wrapped) else ""

            if not target_line:
                return []

            return render_line(typed_line, target_line)

        return UIContent(
            get_line=get_line,
            line_count=len(self.wrapped),
            cursor_position=real.cursor_position,
            show_cursor=real.show_cursor,
        )


class TtypApp():
    def __init__(self, ttyp: Ttyp, to_type: list[str], erase_when_done: bool, debug: bool = False):
        self._ttyp = ttyp
        self._wrapped_to_type = ttyp_wrap(
            to_type=to_type,
            typed_words=[],
            width=10,
        )
        buffer = Buffer(
            on_text_insert=self._on_insert,
            on_cursor_position_changed=self._on_cursor_change
        )
        self._buffer_control = TtypBufferControl(to_type=to_type, buffer=buffer)
        windows = [
            Window(self._buffer_control, wrap_lines=False),
        ]
        self._debug_buffer = Buffer()
        if debug:
            windows.append(
                Window(BufferControl(buffer=self._debug_buffer), wrap_lines=True)
            )
        root_container = HSplit(windows)
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

        return kb

    def _on_cursor_change(self, buffer: Buffer):
        end = len(buffer.text)
        if buffer.cursor_position < end:
            buffer.cursor_position = end

    def _on_insert(self, buffer: Buffer):
        new_cursor_position = self._ttyp.insert_char(
            typed=buffer.text,
            last_char=buffer.document.char_before_cursor,
            cursor_position=buffer.cursor_position,
        )
        # In case a space key is blocked
        if new_cursor_position == buffer.cursor_position - 1:
            buffer.text = buffer.text[:-1]
        buffer.cursor_position = new_cursor_position

        if not self._buffer_control.wrapped:
            return

        doc = buffer.document
        i = doc.cursor_position_row
        if i >= len(self._buffer_control.wrapped):
            return

        # Require number of word is the same and go to next line on space
        typed_line = doc.lines[i]
        typed_words = typed_line.split()
        target_words = self._buffer_control.wrapped[i].split()
        if len(typed_words) == len(target_words) and typed_line.endswith(" "):
            buffer.newline()

        ttyp = self._ttyp
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
        self._debug_buffer.text = str(text) + "\n"
