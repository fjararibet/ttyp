import textwrap


def ttyp_textwrap(text: str, width: int):
    result = textwrap.wrap(text, width=width)
    i = 0
    while i < len(result)-1:
        if len(result[i]) >= width:
            last_word = result[i].split()[-1]
            result[i] = " ".join(result[i].split()[:-1])
            result[i+1] = " ".join([last_word] + result[i+1].split())
        i += 1

    # if result:
    #     if len(result[-1]) >= width-1:
    #         last_word = result[-1].split()[-1]
    #         result[-1] = " ".join(result[-1].split()[:-1])
    #         result.append(last_word)
    return result
