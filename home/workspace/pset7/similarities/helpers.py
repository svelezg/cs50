def lines(a, b):
    """Return lines in both a and b"""

    lines_a = a.splitlines()
    lines_b = b.splitlines()

    # intersection string in both list
    return set(lines_a).intersection(lines_b)


def sentences(a, b):
    """Return sentences in both a and b"""

    from nltk.tokenize import sent_tokenize

    sentences_a = sent_tokenize(a, language='english')
    sentences_b = sent_tokenize(b, language='english')

    return set(sentences_a).intersection(sentences_b)


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""

    substrings_a = []
    substrings_b = []

    # iterates over the string but until lenght - n + 1 (Last character does not count)
    for i in range(len(a) - n + 1):
        new_a = a[i:i+n]
        substrings_a.append(new_a)

    for j in range(len(b) - n + 1):
        new_b = b[j:j+n]
        substrings_b.append(new_b)

    return set(substrings_a).intersection(substrings_b)

