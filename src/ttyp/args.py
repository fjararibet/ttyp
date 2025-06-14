import argparse
from .content import get_available_languages, get_available_quote_languages


def valid_language(language):
    if language not in get_available_languages():
        raise argparse.ArgumentTypeError(
            f"invalid choice: {language!r} (use -L to see valid languages)")
    return language


def valid_quote_language(language):
    if language not in get_available_quote_languages():
        raise argparse.ArgumentTypeError(
            f"invalid choice: {language!r} (use --list-quote-languages to see valid languages)")
    return language


def get_args():
    parser = argparse.ArgumentParser(description="CLI typing test")
    parser.add_argument(
        "-l",
        "--language",
        type=valid_language,
        default="english",
        help="Language"
    )
    parser.add_argument("-c", "--count", type=int, default=25, help="Word count to be typed")
    parser.add_argument(
        "-Q",
        "--quote",
        type=valid_quote_language,
        help="Type a quote in the indicated language"
    )
    parser.add_argument("-L", "--list-languages", action="store_true",
                        help="List available languages")
    parser.add_argument("--list-quote-languages", action="store_true",
                        help="List available quote languages")
    parser.add_argument("-p", "--punctuation", action="store_true", help="Enable punctuation")
    parser.add_argument("-q", "--quiet", action="count", default=0,
                        help="Decrease output, can be used multiple times")
    parser.add_argument("-v", "--verbose", action="count", default=1,
                        help="Increase output, can be used multiple times")
    parser.add_argument("-d", "--debug", action="store_true", help=argparse.SUPPRESS)

    return parser.parse_args()
