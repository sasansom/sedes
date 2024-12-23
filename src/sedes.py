import re
import unicodedata

import hexameter.scan

from known import KNOWN_SCANSIONS
# Normalize Unicode in KNOWN_SCANSIONS.
KNOWN_SCANSIONS = dict(
    (
        unicodedata.normalize("NFD", key),
        tuple((unicodedata.normalize("NFD", word), metrical_shape) for (word, metrical_shape) in value),
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
    scansion = scansion[:]
    while scansion:
        element = scansion.pop(0)
        c, value = element

        if value == "|":
            # This is just a foot marker, ignore it.
            continue

        # If it's a space with punctuation, put the punctuation either at the
        # end of this word or the beginning of the next, depending on what side
        # of the space it's on.
        parts = c.split(" ", 1)
        trimmed = trim(parts[0])
        if trimmed:
            current.append((trimmed, value))
        if (len(parts) == 1 and trimmed != c) or len(parts) > 1:
            # There's a word break here. Yield the current word.
            if current:
                yield current
            current = []
            # If there's something after a space, push it into the scansion
            # queue to be re-handled in the next iteration as the beginning of
            # the next word.
            if len(parts) > 1:
                trimmed = trim(parts[1])
                if trimmed:
                    scansion.insert(0, (trimmed, value))
    if current:
        yield current

def format_metrical_shape(shape):
    """
    Converts the hexameter module's internal long/short notation ('+'/'-') to
    Unicode '–'/'⏑'.
    https://github.com/sasansom/sedes/issues/44
    """
    return "".join({"+": "–", "-": "⏑"}[c] for c in shape)

def extract_diacritic(s):
    """Extracts a diacritic character (acute, grave, or circumflex) from the
    string s. Returns "" if there is no diacritic. Raises ValueError if there
    are more than one diacritic in the string."""
    diacritics = re.findall(r'[\u0300\u0301\u0342]', s)
    if len(diacritics) == 0:
        return ""
    elif len(diacritics) == 1:
        return diacritics[0]
    else:
        raise ValueError(f"multiple tone diacritics: {c!r} {sub_scansion!r}")

def assign(scansion):
    """From a metrical scansion (sequence of (character cluster, preliminary
    metrical analysis, final metrical analysis) tuples as output by
    hexameter.scan.analyze_line_metrical), produce a sequence of (word, sedes,
    metrical_shape, tone_shape) tuples."""
    # Output list of tuples.
    result = []
    # Sedes of the current word -- the first sedes seen after a word break.
    word_sedes = None
    # Buffer of words seen up until a sedes after a word break. This is needed
    # for sequences like "δ’ ἐτελείετο", where the "δ’" inherits the sedes of
    # the following word.
    words = []
    # Buffer of metrical shapes seen up until a sedes after a word break.
    metrical_shapes = []
    # Buffer of tone shapes seen up until a sedes after a word break.
    tone_shapes = []
    sedes = 1.0

    for sub_scansion in partition_scansion_into_words(scansion):
        # List of character clusters making up the current word.
        word = []
        # List of "-" and "+" symbols indicating the metrical shape of the current
        # word.
        metrical_shape = []
        # List of encoded tone shape markers for the tone shape of the current
        # word.
        tone_shape = []
        skipped_diacritic = ""
        for c, value in sub_scansion:
            word.append(c)
            if value in ("-", "+"):
                metrical_shape.append(value)
                if word_sedes is None:
                    # The first vowel in a word, remember the sedes for the whole word.
                    word_sedes = sedes
            # If it's a vowel with a sedes value, advance the sedes counter.
            if value == "-":
                sedes += 0.5
            elif value == "+":
                sedes += 1.0
            # Tone shape.
            diacritic = extract_diacritic(c)
            if value == ".":
                # A value of "." means SKIPPED, which, in hexameter/hexameter.py,
                # is "not used in input, but are used in output analysis".
                # SKIPPED syllables do not have metrical quantity, but they may
                # have a diacritic that we want to preserve for the tone_shape.
                # Remember the skipped_diacritic, to be applied to an
                # immediately succeeding quantity-bearing syllable that has no
                # diacritic of its own.
                skipped_diacritic = diacritic
            else:
                # Make sure we don't have a diacritic that conflicts with a
                # preceding skipped_diacritic.
                assert not (diacritic and skipped_diacritic), (diacritic, skipped_diacritic)
                # If this syllable has no diacritic, inherit an immediately
                # preceding skipped_diacritic.
                diacritic = diacritic or skipped_diacritic
                skipped_diacritic = ""
                t = ""
                if value == "" and diacritic == "":
                    pass
                elif value == "-" and diacritic == "":
                    t = "."   # short, no accent
                elif value == "-" and diacritic == "\u0301": # COMBINING ACUTE ACCENT
                    t = "/"   # short acute
                elif value == "-" and diacritic == "\u0300": # COMBINING GRAVE ACCENT
                    t = "\\"  # short grave
                elif value == "-" and diacritic == "\u0342": # COMBINING GREEK PERISPOMENI
                    t = "~"   # short circumflex
                elif value == "+" and diacritic == "":
                    t = ".-"  # long, no accent
                elif value == "+" and diacritic == "\u0301": # COMBINING ACUTE ACCENT
                    t = "/-"  # long acute
                elif value == "+" and diacritic == "\u0300": # COMBINING GRAVE ACCENT
                    t = "\\-" # long grave
                elif value == "+" and diacritic == "\u0342": # COMBINING GREEK PERISPOMENI
                    t = "~-"  # long circumflex
                else:
                    raise ValueError(f"unknown tone diacritic combination: {(value, diacritic)!a} {sub_scansion!r}")
                tone_shape.append(t)
        assert skipped_diacritic == "", skipped_diacritic
        # Append this word to the list of words that share the current
        # sedes.
        word = "".join(word)
        words.append(word)
        metrical_shape = "".join(metrical_shape)
        metrical_shapes.append(metrical_shape)
        tone_shape = "".join(tone_shape)
        tone_shapes.append(tone_shape)

        if word_sedes is not None:
            # Once we know the sedes, output all the words seen since the
            # last time we saw a sedes.
            for (w, m, t) in zip(words, metrical_shapes, tone_shapes):
                result.append((w, "{:g}".format(word_sedes), format_metrical_shape(m), t))
            words = []
            metrical_shapes = []
            tone_shapes = []
            word_sedes = None

    assert sedes == 13.0, sedes
    assert not words, words
    assert word_sedes is None, word_sedes
    return tuple(result)

def recover_known(text, known):
    """Recovers a sequence of (word, word_n, sedes, metrical_shape, tone_shape)
    from the text of a line and its corresponding sequence of (word, metrical_shape)."""
    # Call hexameter.scan._local_metrical_analysis, which is used internally by
    # hexameter.scan.analyze_line_metrical. Presumably the line doesn't scan,
    # which is why we're looking it up in database of known scansions. But we
    # still use the local metrical analysis in inferring a tone_shape for the
    # words in the line.
    local = hexameter.scan._local_metrical_analysis(text)
    sub_scansions = partition_scansion_into_words(local)
    sedes = 1.0
    result = []
    for (word_n, ((word, metrical_shape), sub_scansion)) in enumerate(zip(known, sub_scansions)):
        # Ignore empty words; this is a hack to permit a line to start at a
        # sedes other than 1, for example when one metrical line is split across
        # multiple printed lines, as in Theoc 5.66–68.
        if word:
            # Isolate the vowels picked out by
            # hexameter.scan._local_metrical_analysis and find the diacritic
            # attached to each.
            tones = []
            for c, value in sub_scansion:
                if value in ("-", "+", "?", "c"):
                    pass
                elif value == "":
                    continue
                else:
                    assert ValueError(f"unknown preliminary scansion value {c!a}")
                diacritic = extract_diacritic(c)
                t = ""
                if diacritic == "":
                    t = "."
                elif diacritic == "\u0301": # COMBINING ACUTE ACCENT
                    t = "/"
                elif diacritic == "\u0300": # COMBINING GRAVE ACCENT
                    t = "\\"
                elif diacritic == "\u0342": # COMBINING GREEK PERISPOMENI
                    t = "~"
                else:
                    raise ValueError(f"unknown diacritic: {diacritic!a} {(c, value)}")
                tones.append(t)
            if len(tones) == len(metrical_shape):
                # If we got the same number of diacritic codes as metrical
                # length codes, create a tone_shape by appending a "-" to the
                # diacritic code for long syllables, and leaving just the
                # diacritic code for short syllables.
                tone_shapes = []
                for t, m in zip(tones, metrical_shape):
                    if m == "-":
                        tone_shapes.append(t)
                    elif m == "+":
                        tone_shapes.append(t + "-")
                    else:
                        raise ValueError(f"unknown metrical shape code {m!a}")
                tone_shape = "".join(tone_shapes)
            else:
                tone_shape = "TODO"
            result.append((word, word_n+1, "{:g}".format(sedes), format_metrical_shape(metrical_shape), tone_shape))
        for value in metrical_shape:
            if value == "-":
                sedes += 0.5
            elif value == "+":
                sedes += 1.0
    return tuple(result)

def analyze(text):
    # First check if this is a hard-coded override.
    known = KNOWN_SCANSIONS.get(text)
    if known is not None:
        return (recover_known(text, known),)
    # Otherwise analyze it.
    result = []
    for scansion in hexameter.scan.analyze_line_metrical(text):
        # Discard the "preliminary metrical analysis" element of each scansion
        # tuple.
        scansion = list((c, value) for (c, prelim, value) in scansion)
        result.append(tuple((word, word_n+1, sedes, metrical_shape, tone_shape) for (word_n, (word, sedes, metrical_shape, tone_shape)) in enumerate(assign(scansion))))
    return result
