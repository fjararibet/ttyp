from random import randint
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.formatted_text import FormattedText


def random_words():
    all_words = []
    word_count = 10
    with open("./words.txt") as f:
        for word in f:
            all_words.append(word.strip("\n"))
    return [all_words[randint(0, len(all_words)-1)] for _ in range(word_count)]


to_write = " ".join(random_words())
text = FormattedText([
    ("#999999", to_write),
])

print(text)

user_text = input()
if user_text == to_write:
    print(FormattedText([("#00cc00", "Sucess!")]))
else:
    print(FormattedText([("#cc0000", "Fail!")]))
