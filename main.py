from random import randint
import time
from prompt_toolkit import print_formatted_text as print, PromptSession
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings


def random_words():
    all_words = []
    word_count = 10
    with open("./words.txt") as f:
        for word in f:
            all_words.append(word.strip("\n"))
    return [all_words[randint(0, len(all_words)-1)] for _ in range(word_count)]


session = PromptSession()
bindings = KeyBindings()
start = -1
words = " ".join(random_words())
to_write = ["#999999", words]
written = ["", ""]
curr_index = 0


@bindings.add("<any>")
def on_key(event):
    global curr_index
    curr_index += 1
    written[1] = written[1] + event.data
    to_write[1] = to_write[1][1:]
    if (len(to_write[1]) == 0):
        event.app.current_buffer.validate_and_handle()
    global start
    if start > 0:
        return
    start = time.time()


@bindings.add("backspace")
def on_backspace(event):
    global curr_index
    curr_index = curr_index - 1 if curr_index > 0 else curr_index
    to_write[1] = words[curr_index:]
    written[1] = written[1][:-1]


def get_prompt():
    return FormattedText([tuple(written), tuple(to_write)])


user_text = session.prompt(get_prompt, key_bindings=bindings)

if written[1] == words:
    total_time_sec = time.time() - start
    wpm = len(words) / 5 * 60 / total_time_sec
    print(FormattedText([("#00cc00", f"wpm {wpm:.0f}")]))

else:
    print(FormattedText([("#cc0000", "Fail!")]))
