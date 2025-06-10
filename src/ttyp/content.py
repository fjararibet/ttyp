from random import randint
from .languages.english import english
from .languages.spanish import spanish


def random_words(language: str, word_count: int):
    all_words = []
    if language == "english":
        all_words = english
    if language == "spanish":
        all_words = spanish
    return [all_words[randint(0, len(all_words)-1)] for _ in range(word_count)]
