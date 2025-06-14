import importlib.resources
from pathlib import Path
import json
from random import random, choice
import sys


def _has_capital(s: str):
    return any(c.isupper() for c in s)


punctuation_marks = [".", ",", ":", ";", "!", "?",]


def random_words(language: str, word_count: int, punctuation: bool):
    package = "ttyp.static.languages"
    with importlib.resources.open_text(package, f'{language}.json') as f:
        data = json.load(f)
        words = data["words"]
        if not punctuation:
            words = [word for word in words if not _has_capital(word)]
        chosen_word_list = [choice(words) for _ in range(word_count)]
        if punctuation:
            chosen_word_list = [
                word + (choice(punctuation_marks) if random() < 0.2 else "")
                for word in chosen_word_list
            ]
            chosen_word_list = [
                word.capitalize() if random() < 0.25 else word
                for word in chosen_word_list
            ]
        return " ".join(chosen_word_list), None


def random_quote(language: str):
    if language not in get_available_quote_languages():
        print("Language not supported for quotes, use --list-quote-languages to see available quote languages")
        sys.exit(1)
    package = "ttyp.static.quotes"
    with importlib.resources.open_text(package, f'{language}.json') as f:
        data = json.load(f)
        quotes = data["quotes"]
        chosen_quote_info = choice(quotes)
        chosen_quote = chosen_quote_info["text"]
        source = chosen_quote_info["source"]
        return chosen_quote, source


def get_available_languages():
    package = "ttyp.static.languages"
    with importlib.resources.files(package) as data_dir:
        return [
            Path(entry.name).stem
            for entry in data_dir.iterdir()
            if entry.name != "__init__.py"
        ]


def get_available_quote_languages():
    package = "ttyp.static.quotes"
    with importlib.resources.files(package) as data_dir:
        return [
            Path(entry.name).stem
            for entry in data_dir.iterdir()
            if entry.name != "__init__.py"
        ]


def get_file_content(filename: str):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().replace("\n", " "), None
    except OSError as e:
        print(f"Could not read file '{filename}': {e}")
        sys.exit(1)
