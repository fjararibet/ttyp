from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from prompt_toolkit.document import Document
from random import randint
import time


class Ttype():
    def __init__(self, to_write: [str]):
        self.written: str = []
        self.to_write: [str] = to_write

    def add_word(self, word: str):
        self.written.append(word)

    def set_written(self, written: str):
        self.written = written

    def _number_of_correct_chars(self, typed: str):
        result = 0
        for typed_word, correct_word in zip(typed, self.to_write):
            if typed_word == correct_word:
                result += len(typed_word)
                continue
            for i, j in zip(typed_word, correct_word):
                if i != j:
                    continue
                result += 1
        return result

    def get_wpm(self, typed: str, elapsed):
        correct_chars = self._number_of_correct_chars(typed)
        wpm = correct_chars / 5 * 60 / elapsed
        return wpm


class TtypeLexer(Lexer):
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


def random_words():
    all_words = []
    word_count = 10
    with open("./words.txt") as f:
        for word in f:
            all_words.append(word.strip("\n"))
    return [all_words[randint(0, len(all_words)-1)] for _ in range(word_count)]


to_write = random_words()
lexer = TtypeLexer(to_write)


ttype = Ttype(to_write)


def on_change(buffer: Buffer):
    global start
    if not start:
        start = time.time()
    typed = buffer.text.split()
    if len(typed) >= len(to_write) and typed[-1] == to_write[-1]:
        elapsed = time.time() - start
        wpm = ttype.get_wpm(typed, elapsed)
        buffer.app.exit(result=wpm)


buffer = Buffer(on_text_changed=on_change)

kb = KeyBindings()

start = None


@kb.add('c-c')
def exit_(event: KeyPressEvent):
    event.app.exit()


@kb.add('enter')
def disable_enter(event: KeyPressEvent):
    pass


root_container = HSplit([
    Window(BufferControl(buffer=buffer, lexer=lexer))
])

layout = Layout(root_container)

style = Style.from_dict({
    "ghost": "#999999",
    "wrong": "#cc0000",
    "written": "",
})

app = Application(
    layout=layout,
    key_bindings=kb,
    full_screen=False,
    style=style
)
buffer.app = app

if __name__ == '__main__':
    result = app.run()
    if result:
        print(f"wpm {result:.1f}")
