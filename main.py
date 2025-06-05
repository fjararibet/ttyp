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
        self.written = ""
        self.to_write = to_write

    def add_char(self, char):
        self.written += char

    def lex_document(self, document: Document):
        text = document.text

        def get_line(lineno):
            line = document.lines[lineno]
            tokens = []
            for written_word, to_write_word in zip(self.written.split(), self.to_write):
                if written_word == to_write_word:
                    tokens.append(("class:written", written_word))
                    tokens.append(("", " "))
                    continue
                # char by char
                longest_word_len = len(max(written_word, to_write_word))
                shortest_word_len = len(min(written_word, to_write_word))
                for i in range(longest_word_len):
                    if i < shortest_word_len:
                        if written_word[i] == to_write_word[i]:
                            tokens.append(("class:written", written_word[i]))
                        else:
                            tokens.append(("class:wrong", written_word[i]))
                    else:
                        tokens.append(("class:ghost", to_write_word[i]))
                tokens.append(("", " "))
            for i, word in enumerate(self.to_write):
                if i < len(self.written.split()):
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
def on_insert(buffer):
    lexer.add_char(buffer.text[-1])
buffer = Buffer(on_text_insert=on_insert)

# Key bindings
kb = KeyBindings()


@kb.add('c-c')
def exit_(event):
    event.app.exit()


# buffer.text = " ".join(to_write)

# Layout
root_container = HSplit([
    Window(BufferControl(buffer=buffer, lexer=lexer))
])

layout = Layout(root_container)

# Style definitions
style = Style.from_dict({
    "ghost": "#999999",
    "wrong": "#cc0000",
    "written": "",
})

# Application
app = Application(
    layout=layout,
    key_bindings=kb,
    full_screen=False,
    style=style
)

if __name__ == '__main__':
    app.run()
