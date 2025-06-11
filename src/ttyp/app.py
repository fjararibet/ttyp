from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from prompt_toolkit.document import Document
import time
from .ttyp import Ttyp


class TtypLexer(Lexer):
    def __init__(self, to_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.to_type = to_type

    def lex_document(self, document: Document):

        def get_line(lineno):
            line = document.lines[lineno]
            tokens = []
            # here it needs to be word by word instead of char by char
            # to account for extra letters the user might have typed
            # in a word.
            for typed_word, word_to_type in zip(line.split(), self.to_type.split()):
                # char by char
                min_len = min(len(typed_word), len(word_to_type))
                for i, j in zip(typed_word, word_to_type):
                    style = "typed" if i == j else "wrong"
                    tokens.append((f"class:{style}", i))

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
            for i, word in enumerate(self.to_type.split()[typed_wcount:]):
                tokens.append(("class:ghost", word))
                tokens.append(("", " "))

            return tokens

        return get_line


class TtypBuffer(Buffer):
    def __init__(self, ttyp: Ttyp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ttyp = ttyp


class TtypApp():
    def __init__(self, ttyp: Ttyp, to_type: [str]):
        self._to_type = to_type
        buffer = TtypBuffer(ttyp=ttyp, on_text_changed=self.on_change,
                            on_text_insert=self.on_insert)
        lexer = TtypLexer(to_type=to_type)
        root_container = HSplit([
            Window(BufferControl(buffer=buffer, lexer=lexer), wrap_lines=True)
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
            style=style
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

    def on_change(self, buffer: TtypBuffer):
        ttyp = buffer.ttyp
        if not ttyp._start:
            ttyp._start = time.time()
        ttyp.set_typed(buffer.text)
        if ttyp.is_done():
            wpm = ttyp.get_wpm()
            acc = ttyp.get_acc()
            self._app.exit(result={"wpm": wpm, "acc": acc})

    def on_insert(self, buffer: TtypBuffer):
        typed = buffer.text
        ttyp = buffer.ttyp
        cursor_position = buffer.cursor_position
        new_cursor_position = ttyp.insert_char(typed, cursor_position)
        diff = new_cursor_position - cursor_position
        # cursor can't be moved if the buffer is not big enough,
        # so spaces are added
        buffer.text += " " * diff
        buffer.cursor_position = new_cursor_position
