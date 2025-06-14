from prompt_toolkit import print_formatted_text as print
from .args import get_args
from .ttyp import Ttyp
from .content import random_words, get_available_languages, random_quote
from .app import TtypApp


def main():
    args = get_args()
    if args.list_languages:
        languages = get_available_languages()
        print("\n".join(languages))
        return
    verbosity_level = args.verbose - args.quiet
    to_type, source = (
        random_words(args.language, args.count, args.punctuation) if not args.quote
        else random_quote(args.quote)
    )
    ttyp = Ttyp(to_type=to_type)
    app = TtypApp(
        to_type=to_type,
        ttyp=ttyp,
        erase_when_done=verbosity_level <= 0,
        debug=args.debug
    )
    result = app.run()
    if result and verbosity_level >= 0:
        wpm = result.get("wpm")
        acc = result.get("acc")
        print(f"wpm {wpm:.1f}")
        print(f"acc {acc*100:.1f}%")

    if result and verbosity_level >= 2:
        correct = result.get("correct")
        mistakes = result.get("mistakes")
        print(f"mistakes {mistakes}")
        print(f"correct {correct}")
    if result and args.quote and verbosity_level >= 1:
        print(f"source {source}")


if __name__ == '__main__':
    main()
