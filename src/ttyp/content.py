import importlib.resources
from pathlib import Path
import json
from random import randint


def random_words(language: str, word_count: int):
    package = "ttyp.static.languages"
    with importlib.resources.open_text(package, f'{language}.json') as f:
        data = json.load(f)
        chosen_word_list = [
            data["words"][randint(0, len(data["words"])-1)]
            for _ in range(word_count)
        ]
        return " ".join(chosen_word_list), None


def random_quote(language: str):
    package = "ttyp.static.quotes"
    with importlib.resources.open_text(package, f'{language}.json') as f:
        data = json.load(f)
        quotes = data["quotes"]
        chosen_quote_info = quotes[randint(0, len(quotes)-1)]
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
