from prompt_toolkit import print_formatted_text as print
from .args import get_args
from .ttyp import Ttyp
from .content import random_words, get_available_languages
from .app import TtypApp


def main():
    args = get_args()
    if args.list_languages:
        languages = get_available_languages()
        print("\n".join(languages))
        return
    to_type = random_words(language=args.language, word_count=args.count)
    ttyp = Ttyp(to_type=to_type)
    app = TtypApp(to_type=to_type, ttyp=ttyp)
    result = app.run()
    if result:
        wpm = result.get("wpm")
        acc = result.get("acc")
        print(f"\n{wpm:.1f} wpm")
        print(f"{acc*100:.1f}% acc")


if __name__ == '__main__':
    main()
