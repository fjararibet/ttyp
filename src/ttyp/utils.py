import textwrap


def ttyp_textwrap(text: str, width: int):
    result = textwrap.wrap(text, width=width)
    i = 0
    while i < len(result)-1:
        while len(result[i]) >= width:
            last_word = result[i].split()[-1]
            result[i] = " ".join(result[i].split()[:-1])
            result[i+1] = " ".join([last_word] + result[i+1].split())
        i += 1

    if result:
        new_line_words = []
        while len(result[-1]) >= width:
            last_word = result[-1].split()[-1]
            result[-1] = " ".join(result[-1].split()[:-1])
            new_line_words.append(last_word)
        if new_line_words:
            result.append(" ".join(new_line_words))
    return result
