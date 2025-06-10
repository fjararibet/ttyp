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
    def __init__(self, to_write, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.to_write = to_write

    def lex_document(self, document: Document):

        def get_line(lineno):
            line = document.lines[lineno]
            tokens = []
            for written_word, to_write_word in zip(line.split(), self.to_write):
                if written_word == to_write_word:
                    tokens.append(("class:written", written_word))
                    tokens.append(("", " "))
                    continue

                # char by char
                min_len = min(len(written_word), len(to_write_word))
                for i, j in zip(written_word, to_write_word):
                    style = "written" if i == j else "wrong"
                    tokens.append((f"class:{style}", i))

                # leftover written word
                for c in written_word[min_len:]:
                    style = "wrong"
                    tokens.append((f"class:{style}", c))

                # leftover target word
                for c in to_write_word[min_len:]:
                    style = "ghost"
                    tokens.append((f"class:{style}", c))

                tokens.append(("", " "))
            for i, word in enumerate(self.to_write):
                if i < len(line.split()):
                    continue
                tokens.append(("class:ghost", word))
                tokens.append(("", " "))

            return tokens

        return get_line


class TtypBuffer(Buffer):
    def __init__(self, ttyp: Ttyp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ttyp = ttyp


class TtypApp():
    def __init__(self, ttyp: Ttyp, to_write: [str]):
        self._to_write = to_write
        buffer = TtypBuffer(ttyp=ttyp, on_text_changed=self.on_change,
                            on_text_insert=self.on_insert)
        lexer = TtypLexer(to_write=to_write)
        root_container = HSplit([
            Window(BufferControl(buffer=buffer, lexer=lexer), wrap_lines=True)
        ])
        layout = Layout(root_container)

        style = Style.from_dict({
            "ghost": "#999999",
            "wrong": "#cc0000",
            "written": "",
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
        typed = buffer.text.split()
        if len(typed) >= len(self._to_write) and typed[-1] == self._to_write[-1]:
            wpm = ttyp.get_wpm(typed)
            acc = ttyp.get_acc(typed)
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
        buffer.cursor_position += diff
