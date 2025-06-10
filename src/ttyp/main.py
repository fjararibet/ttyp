from .args import get_args
from .ttyp import Ttyp
from .content import random_words
from .app import TtypApp


def main():
    args = get_args()
    to_write = random_words(language=args.language, word_count=args.count)
    ttyp = Ttyp(to_write=to_write)
    app = TtypApp(to_write=to_write, ttyp=ttyp)
    result = app.run()
    if result:
        wpm = result.get("wpm")
        acc = result.get("acc")
        print(f"\n{wpm:.1f} wpm")
        print(f"{acc*100:.1f}% acc")


if __name__ == '__main__':
    main()
