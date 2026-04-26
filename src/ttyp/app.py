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
        typed = self.buffer.text

        wrapped = textwrap.wrap(
            " ".join(self.to_type),
            width=width-1,
            break_long_words=False,
            break_on_hyphens=False,
        )
        total = max(real.line_count, len(wrapped))

        def get_line(lineno):
            if lineno >= len(self.buffer.document.lines):
                return []
            line = self.buffer.document.lines[lineno]
            tokens = []

            for line, to_type_line in zip(self.buffer.document.lines, wrapped):
            
                # here it needs to be word by word instead of char by char
                # to account for extra letters the user might have typed
                # in a word.
                for typed_word, word_to_type in zip(line.split(), to_type_line.split()):
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
                typed_wcount = len(line.split())
                leftover = to_type_line.split()[typed_wcount:]
                for i, word in enumerate(leftover):
                    tokens.append(("class:ghost", word))
                    if i < len(leftover) - 1:
                        tokens.append(("", " "))
                        continue
                    

            return tokens

        return UIContent(
            get_line=get_line,
            line_count=total,
            cursor_position=real.cursor_position,
            show_cursor=real.show_cursor,
        )


class TtypLexer(Lexer):
    def __init__(self, to_type: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.to_type = to_type

    def lex_document(self, document: Document):

        def get_line(lineno):
            line = document.lines[lineno]
            tokens = []

            cols = get_app().output.get_size().columns
            wrapped = textwrap.wrap(
                " ".join(self.to_type),
                width=cols-1,
                break_long_words=False,
                break_on_hyphens=False,
                replace_whitespace=False,
                drop_whitespace=True,
            )
            for line, to_type_line in zip(document.lines, wrapped):
            
                # here it needs to be word by word instead of char by char
                # to account for extra letters the user might have typed
                # in a word.
                for typed_word, word_to_type in zip(line.split(), to_type_line.split()):
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
                typed_wcount = len(line.split())
                leftover = to_type_line.split()[typed_wcount:]
                for i, word in enumerate(leftover):
                    print(word)
                    tokens.append(("class:ghost", word))
                    if i < len(leftover) - 1:
                        tokens.append(("", " "))
                        continue
                    

            return tokens

        return get_line


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
        lexer = TtypLexer(to_type=to_type)
        root_container = HSplit([
            Window(GhostBufferControl(to_type=to_type, buffer=buffer, lexer=None), wrap_lines=False),
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
