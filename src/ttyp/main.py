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
from .args import get_args
from .languages.english import english
from .languages.spanish import spanish


class Ttyp():
    def __init__(self, to_write: [str]):
        self.written: str = []
        self.to_write: [str] = to_write
        self.mistakes: int = 0

    def add_word(self, word: str):
        self.written.append(word)

    def set_written(self, written: str):
        self.written = written

    def insert_char(self, typed: str, cursor_position: int):
        """Should be called on all inserted chars, even if they
        are later deleted, so the mistake tracking is accurate.
        """
        last_inserted_char = typed[cursor_position-1]
        if (last_inserted_char == " "):
            to_write_text = " ".join(self.to_write)
            next_space_pos = to_write_text.find(" ", cursor_position-1)
            if next_space_pos != cursor_position-1:
                self.mistakes += next_space_pos - cursor_position + 1
            return next_space_pos + 1
        typed_words = typed.split()
        if len(typed_words) == 0:
            return cursor_position
        last_typed_word = typed_words[-1]
        if (len(typed_words) > len(self.to_write)):
            return cursor_position
        curr_target_word = self.to_write[len(typed_words)-1]
        if (len(last_typed_word) > len(curr_target_word)):
            self.mistakes += 1
            return cursor_position

        if (last_inserted_char != curr_target_word[len(last_typed_word)-1]):
            self.mistakes += 1
        return cursor_position

    def _number_of_correct_chars(self, typed: str):
        result = 0
        for typed_word, correct_word in zip(typed, self.to_write):
            if typed_word == correct_word:
                result += len(typed_word) + 1  # account for space
                continue
            for i, j in zip(typed_word, correct_word):
                if i != j:
                    continue
                result += 1
        # A space each counted for each word,
        # but the last one doesn't have a space
        if typed[-1] == self.to_write[-1]:
            result -= 1
        return result

    def _number_of_incorrect_chars(self, typed: str):
        result = 0
        for typed_word, correct_word in zip(typed, self.to_write):
            if typed_word == correct_word:
                continue
            for i, j in zip(typed_word, correct_word):
                if i != j:
                    continue
                result += 1
            # remaing errors if they exists
            min_len = min(len(typed_word), len(correct_word))
            for c in typed_word[min_len:]:
                result += 1

        return result

    def get_wpm(self, typed: str, elapsed):
        correct_chars = self._number_of_correct_chars(typed)
        wpm = correct_chars / 5 * 60 / elapsed
        return wpm

    def get_acc(self, typed: str):
        correct_chars = self._number_of_correct_chars(typed)
        incorrect_chars = self.mistakes
        return correct_chars / (correct_chars + incorrect_chars)


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


def random_words(language: str, word_count: int):
    all_words = []
    if language == "english":
        all_words = english
    if language == "spanish":
        all_words = spanish
    return [all_words[randint(0, len(all_words)-1)] for _ in range(word_count)]


def main():
    args = get_args()
    to_write = random_words(language=args.language, word_count=args.count)
    lexer = TtypLexer(to_write)

    ttyp = Ttyp(to_write)

    def on_change(buffer: Buffer):
        global start
        if not buffer.start:
            buffer.start = time.time()
        typed = buffer.text.split()
        if len(typed) >= len(to_write) and typed[-1] == to_write[-1]:
            elapsed = time.time() - buffer.start
            wpm = ttyp.get_wpm(typed, elapsed)
            acc = ttyp.get_acc(typed)
            buffer.app.exit(result={"wpm": wpm, "acc": acc})

    def on_insert(buffer: Buffer):
        typed = buffer.text
        cursor_position = buffer.cursor_position
        new_cursor_position = ttyp.insert_char(typed, cursor_position)
        diff = new_cursor_position - cursor_position
        buffer.text += " " * diff
        buffer.cursor_position += diff

    buffer = Buffer(on_text_changed=on_change, on_text_insert=on_insert)

    kb = KeyBindings()

    @kb.add('c-c')
    def exit_(event: KeyPressEvent):
        event.app.exit()

    @kb.add('enter')
    def disable_enter(event: KeyPressEvent):
        pass

    root_container = HSplit([
        Window(BufferControl(buffer=buffer, lexer=lexer), wrap_lines=True)
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
    buffer.start = None
    result = app.run()
    if result:
        wpm = result.get("wpm")
        acc = result.get("acc")
        print(f"\n{wpm:.1f} wpm")
        print(f"{acc*100:.1f}% acc")


if __name__ == '__main__':
    main()
