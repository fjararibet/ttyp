import time


class Ttyp():
    """Handle all game state"""

    def __init__(self, to_type: list[str]):
        self._to_type = to_type
        self._mistakes: int = 0
        self._start: float | None = None

    def get_mistakes(self):
        return self._mistakes

    def get_correct(self, typed: str):
        return self._number_of_correct_chars(typed)

    def is_done(self, typed: str, cursor_position: int):
        if not typed.strip():
            return
        typed_words = typed.split()
        in_final_word = len(typed_words) >= len(self._to_type)

        is_final_word_correct = typed_words[-1] == self._to_type[-1]
        is_space_in_final_word = typed[cursor_position-1] == " "
        final_word_ended = is_final_word_correct or is_space_in_final_word

        return in_final_word and final_word_ended

    def insert_char(self, typed: str, last_char: str, cursor_position: int) -> int:
        if not self._start:
            self._start = time.time()
        typed_words = typed.split()
        if (last_char == " "):
            correctly_typed = len(typed_words[-1]) == len(self._to_type[len(typed_words)-1])
            if correctly_typed:
                return cursor_position
            return cursor_position - 1

        if len(typed_words) == 0:
            return cursor_position

        last_typed_word = typed_words[-1]
        if (len(typed_words) > len(self._to_type)):
            return cursor_position

        curr_target_word = self._to_type[len(typed_words)-1]
        if (len(last_typed_word) > len(curr_target_word)):
            self._mistakes += 1
            return cursor_position

        if (last_char != curr_target_word[len(last_typed_word)-1]):
            self._mistakes += 1
        return cursor_position

    def _number_of_correct_chars(self, typed: str):
        """Counts the correctly typed characters at the end of the test"""
        result = 0
        for typed_word, correct_word in zip(typed.split(), self._to_type):
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

    def get_wpm(self, typed: str):
        if not self._start:
            raise RuntimeError("Start time not set")
        elapsed = time.time() - self._start
        correct_chars = self._number_of_correct_chars(typed)
        wpm = correct_chars / 5 * 60 / elapsed
        return wpm

    def get_acc(self, typed: str):
        correct_chars = self._number_of_correct_chars(typed)
        incorrect_chars = self._mistakes
        return correct_chars / (correct_chars + incorrect_chars)
