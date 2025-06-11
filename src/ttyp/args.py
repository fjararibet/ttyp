import argparse
from .content import get_available_languages


def valid_language(language):
    if language not in get_available_languages():
        raise argparse.ArgumentTypeError(
            f"invalid choice: {language!r} (use -L to see valid languages)")
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
    parser.add_argument("-L", "--list-languages", action="store_true",
                        help="List available languages")

    return parser.parse_args()
