import argparse


def get_args():
    parser = argparse.ArgumentParser(description="CLI typing test")
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="english",
        help="Language"
    )
    parser.add_argument("--count", type=int, default=25, help="Word count to be typed")

    return parser.parse_args()
