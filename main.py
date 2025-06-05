from random import randint


def random_words():
    all_words = []
    word_count = 10
    with open("./words.txt") as f:
        for word in f:
            all_words.append(word.strip("\n"))
    return [all_words[randint(0, len(all_words)-1)] for _ in range(word_count)]


to_write = " ".join(random_words())
print(to_write)
user_text = input()
if user_text == to_write:
    print("Sucess!")
else:
    print("Fail!")
