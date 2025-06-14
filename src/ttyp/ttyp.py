import time


class Ttyp():
    """Handle all game state"""

    def __init__(self, to_type: str):
        self._typed: str = ""
        self._to_type: str = to_type
        self._mistakes: int = 0
        self._start = None
        self._cursor_position: int = 0

    def set_typed(self, typed: str):
        backspace = len(typed) == len(self._typed) - 1
        self._typed = typed
        if backspace:
            self._on_backspace()

    def set_cursor_position(self, cursor_position: int):
        self._cursor_position = cursor_position

    def get_cursor_position(self):
        return self._cursor_position

    def get_typed(self):
        return self._typed

    def get_mistakes(self):
        return self._mistakes

    def get_correct(self):
        return self._number_of_correct_chars()

    def _on_backspace(self):
        self._typed = self._typed.rstrip()
        self._cursor_position = len(self._typed)

    def is_done(self):
        if not self._typed.strip():
            return
        typed_words = self._typed.split()
        in_final_word = len(typed_words) >= len(self._to_type.split())

        is_final_word_correct = typed_words[-1] == self._to_type.split()[-1]
        is_space_in_final_word = self._typed[self._cursor_position-1] == " "
        final_word_ended = is_final_word_correct or is_space_in_final_word

        return in_final_word and final_word_ended

    def insert_char(self):
        if not self._start:
            self._start = time.time()
        last_inserted_char = self._typed[self._cursor_position-1]
        typed_words = self._typed.split()
        if (last_inserted_char == " "):
            start_of_word = (
                len(self._typed) >= 2
                and self._typed[self._cursor_position-2] == " "
            )
            start_of_test = len(self._typed.strip()) == 0
            if start_of_word or start_of_test:
                # keep cursor in place
                self._cursor_position -= 1
                return

            correctly_typed = len(typed_words[-1]) == len(self._to_type.split()[len(typed_words)-1])
            if correctly_typed:
                return

            # go to next word
            typed_wcount = len(self._typed.split())
            to_type_wcount = 0
            next_space_pos = 0
            for c in self._to_type:
                if to_type_wcount >= typed_wcount:
                    break
                next_space_pos += 1
                if c == " ":
                    to_type_wcount += 1
            if next_space_pos > self._cursor_position-1:
                self._mistakes += next_space_pos - self._cursor_position
                self._cursor_position = next_space_pos
            return
        if len(typed_words) == 0:
            return
        last_typed_word = typed_words[-1]
        if (len(typed_words) > len(self._to_type.split())):
            return
        curr_target_word = self._to_type.split()[len(typed_words)-1]
        if (len(last_typed_word) > len(curr_target_word)):
            self._mistakes += 1
            return

        if (last_inserted_char != curr_target_word[len(last_typed_word)-1]):
            self._mistakes += 1

    def _number_of_correct_chars(self):
        """Counts the correctly typed characters at the end of the test"""
        result = 0
        for typed_word, correct_word in zip(self._typed.split(), self._to_type.split()):
            if typed_word == correct_word:
                result += len(typed_word) + 1  # account for space
                continue
            for i, j in zip(typed_word, correct_word):
                if i != j:
                    continue
                result += 1
        # A space is counted for each word,
        # but the last one doesn't have a space after
        result -= 1
        return result

    def get_wpm(self):
        elapsed = time.time() - self._start
        correct_chars = self._number_of_correct_chars()
        wpm = correct_chars / 5 * 60 / elapsed
        return wpm

    def get_acc(self):
        correct_chars = self._number_of_correct_chars()
        incorrect_chars = self._mistakes
        return correct_chars / (correct_chars + incorrect_chars)
