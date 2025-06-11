import time


class Ttyp():
    """Handle all game state"""

    def __init__(self, to_type: [str]):
        self._typed: str
        self._to_type: [str] = to_type
        self.mistakes: int = 0
        self._start = None

    def set_typed(self, typed: str):
        self._typed = typed

    def is_done(self):
        typed_words = self._typed.split()
        in_final_word = len(typed_words) >= len(self._to_type.split())
        final_word_ended = typed_words[-1] == self._to_type.split()[-1] or self._typed[-1] == " "
        return in_final_word and final_word_ended

    def insert_char(self, typed: str, cursor_position: int):
        if not self._start:
            self._start = time.time()
        last_inserted_char = typed[cursor_position-1]
        typed_words = typed.split()
        if (last_inserted_char == " "):
            if typed_words[-1] == self._to_type.split()[len(typed_words)-1]:
                return cursor_position
            typed_wcount = len(self._typed.split())
            to_type_wcount = 0
            next_space_pos = 0
            for c in self._to_type:
                if to_type_wcount >= typed_wcount:
                    break
                next_space_pos += 1
                if c == " ":
                    to_type_wcount += 1
            if next_space_pos > cursor_position-1:
                self.mistakes += next_space_pos - cursor_position
                return next_space_pos
            else:
                return cursor_position
        if len(typed_words) == 0:
            return cursor_position
        last_typed_word = typed_words[-1]
        if (len(typed_words) > len(self._to_type.split())):
            return cursor_position
        curr_target_word = self._to_type.split()[len(typed_words)-1]
        if (len(last_typed_word) > len(curr_target_word)):
            self.mistakes += 1
            return cursor_position

        if (last_inserted_char != curr_target_word[len(last_typed_word)-1]):
            self.mistakes += 1
        return cursor_position

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
        incorrect_chars = self.mistakes
        return correct_chars / (correct_chars + incorrect_chars)
