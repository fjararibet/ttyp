import time

class Ttyp():
    """Handle all game state"""

    def __init__(self, to_write: [str]):
        self.written: str = []
        self.to_write: [str] = to_write
        self.mistakes: int = 0
        self._start = None

    def add_word(self, word: str):
        self.written.append(word)

    def set_written(self, written: str):
        self.written = written

    def insert_char(self, typed: str, cursor_position: int):
        """Should be called on all inserted chars, even if they
        are later deleted, so the mistake tracking is accurate.
        """
        if not self._start:
            self._start = time.time()
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

    def get_wpm(self, typed: str):
        elapsed = time.time() - self._start
        correct_chars = self._number_of_correct_chars(typed)
        wpm = correct_chars / 5 * 60 / elapsed
        return wpm

    def get_acc(self, typed: str):
        correct_chars = self._number_of_correct_chars(typed)
        incorrect_chars = self.mistakes
        return correct_chars / (correct_chars + incorrect_chars)
