import re
import unicodedata

import hexameter.scan

from known import KNOWN_SCANSIONS
# Normalize Unicode in KNOWN_SCANSIONS.
KNOWN_SCANSIONS = dict(
    (
        unicodedata.normalize("NFD", key),
        tuple((unicodedata.normalize("NFD", word), shape) for (word, shape) in value),
    )
    for key, value in KNOWN_SCANSIONS.items()
)

def trim(s):
    return re.sub("[^\\w\u0313\u0314\u0301\u0342\u0300\u0308\u0345\u0323\u2019]*", "", s)

# Yields sub-iterators for each contiguous group of scansion elements that
# belong to the same word, throwing away all punctuation and non-letter
# elements.
def partition_scansion_into_words(scansion):
    current = []
    scansion = list(scansion)
    while scansion:
        element = scansion.pop(0)
        c, mid, value = element

        if value == "|":
            # This is just a foot marker, ignore it.
            continue

        # If it's a space with punctuation, put the punctuation either at the
        # end of this word or the beginning of the next, depending on what side
        # of the space it's on.
        parts = c.split(" ", 1)
        trimmed = trim(parts[0])
        if trimmed:
            current.append((trimmed, mid, value))
        if (len(parts) == 1 and trimmed != c) or len(parts) > 1:
            # There's a word break here. Yield the current word.
            if current:
                yield tuple(current)
            current = []
            # If there's something after a space, push it into the scansion
            # queue to be re-handled in the next iteration as the beginning of
            # the next word.
            if len(parts) > 1:
                trimmed = trim(parts[1])
                if trimmed:
                    scansion.insert(0, (trimmed, mid, value))
    if current:
        yield tuple(current)

def format_shape(shape):
    """
    Converts the hexameter module's internal long/short notation ('+'/'-') to
    Unicode '–'/'⏑'.
    https://github.com/sasansom/sedes/issues/44
    """
    return "".join({"+": "–", "-": "⏑"}[c] for c in shape)

def assign(scansion):
    """From a metrical scansion (sequence of (character cluster, preliminary
    metrical analysis, final metrical analysis) tuples as output by
    hexameter.scan.analyze_line_metrical), produce a sequence of (word, sedes,
    shape) tuples."""
    # Output list of tuples.
    result = []
    # Sedes of the current word -- the first sedes seen after a word break.
    word_sedes = None
    # Buffer of words seen up until a sedes after a word break. This is needed
    # for sequences like "δ’ ἐτελείετο", where the "δ’" inherits the sedes of
    # the following word.
    words = []
    # Buffer of metrical shapes seen up until a sedes after a word break.
    shapes = []
    sedes = 1.0

    for sub_scansion in partition_scansion_into_words(scansion):
        # List of character clusters making up the current word.
        word = []
        # List of "-" and "+" symbols indicating the metrical shape of the current
        # word.
        shape = []
        for c, _, value in sub_scansion:
            word.append(c)
            if value in ("-", "+"):
                shape.append(value)
                if word_sedes is None:
                    # The first vowel in a word, remember the sedes for the whole word.
                    word_sedes = sedes
            # If it's a vowel with a sedes value, advance the sedes counter.
            if value == "-":
                sedes += 0.5
            elif value == "+":
                sedes += 1.0
        # Append this word to the list of words that share the current
        # sedes.
        word = "".join(word)
        words.append(word)
        shape = "".join(shape)
        shapes.append(shape)

        if word_sedes is not None:
            # Once we know the sedes, output all the words seen since the
            # last time we saw a sedes.
            for (w, s) in zip(words, shapes):
                result.append((w, "{:g}".format(word_sedes), format_shape(s)))
            words = []
            shapes = []
            word_sedes = None

    assert sedes == 13.0, sedes
    assert not words, words
    assert word_sedes is None, word_sedes
    return tuple(result)

def recover_known(known):
    """Recovers a sequence of (word, word_n, sedes, shape) from a sequence of
    (word, shape)."""
    sedes = 1.0
    result = []
    for (word_n, (word, shape)) in enumerate(known):
        # Ignore empty words; this is a hack to permit a line to start at a
        # sedes other than 1, for example when one metrical line is split across
        # multiple printed lines, as in Theoc 5.66–68.
        if word:
            result.append((word, word_n+1, "{:g}".format(sedes), format_shape(shape)))
        for value in shape:
            if value == "-":
                sedes += 0.5
            elif value == "+":
                sedes += 1.0
    return tuple(result)

def analyze(text):
    # First check if this is a hard-coded override.
    known = KNOWN_SCANSIONS.get(text)
    if known is not None:
        return (recover_known(known),)
    # Otherwise analyze it.
    result = []
    for scansion in hexameter.scan.analyze_line_metrical(text):
        result.append(tuple((word, word_n+1, sedes, shape) for (word_n, (word, sedes, shape)) in enumerate(assign(scansion))))
    return result
