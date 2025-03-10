import collections

Entry = collections.namedtuple("Entry", (
    "word_n", "word", "lemma",
))

def merge_word(entries, work, book_n, line_n):
    return tuple(((i, entry.word_n),) for i, entry in enumerate(entries))
