from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from prompt_toolkit.document import Document
from random import randint


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


buffer = Buffer()

kb = KeyBindings()


@kb.add('c-c')
def exit_(event):
    event.app.exit()


@kb.add('enter')
def exit_(event):
    """
    Disable enter
    """
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

if __name__ == '__main__':
    app.run()
