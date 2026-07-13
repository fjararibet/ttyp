from prompt_toolkit import print_formatted_text as print
import sys
from .args import get_args
from .ttyp import Ttyp
from .content import (
    random_words,
    get_available_languages,
    get_file_content,
)
from .app import TtypApp
import importlib.metadata


def main():
    args = get_args()
    if args.version:
        print(importlib.metadata.version("ttyp"))
        return
    if args.list_languages:
        languages = get_available_languages()
        print("\n".join(languages))
        return
    verbosity_level = args.verbose - args.quiet
    to_type, _ = (
        get_file_content(args.filepath)
        if args.filepath
        else random_words(args.language, args.count, args.punctuation),
        None,
    )
    ttyp = Ttyp(to_type=to_type)
    app = TtypApp(
        to_type=to_type,
        ttyp=ttyp,
        erase_when_done=verbosity_level <= 0,
        debug=args.debug,
        flip_colors=args.flip_colors,
    )
    result = app.run()
    if result and verbosity_level >= 0:
        wpm = result.get("wpm")
        acc = result.get("acc")
        print(f"wpm {wpm:.1f}", file=sys.stderr)
        print(f"acc {acc * 100:.1f}%", file=sys.stderr)

    if result and verbosity_level >= 2:
        correct = result.get("correct")
        mistakes = result.get("mistakes")
        print(f"mistakes {mistakes}", file=sys.stderr)
        print(f"correct {correct}", file=sys.stderr)

if __name__ == "__main__":
    main()
