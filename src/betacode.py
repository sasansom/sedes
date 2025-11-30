# Beta Code decoding and encoding for Greek.
#
# http://www.stoa.org/unicode/
# http://www.tlg.uci.edu/encoding/quickbeta.pdf
# https://web.archive.org/web/20151104201807/http://www.tlg.uci.edu/~opoudjis/unicode/unicode.html

import functools
import unicodedata

__all__ = ["decode"]

BETA_LETTER_MAP = {
     "a": "α",
    "*a": "Α",
     "b": "β",
    "*b": "Β",
     "c": "ξ",
    "*c": "Ξ",
     "d": "δ",
    "*d": "Δ",
     "e": "ε",
    "*e": "Ε",
     "f": "φ",
    "*f": "Φ",
     "g": "γ",
    "*g": "Γ",
     "h": "η",
    "*h": "Η",
     "i": "ι",
    "*i": "Ι",
    # Wikipedia: "Some representations use J for the final sigma..."
    # "j": "ς",
    # No capital form of "j".
     "k": "κ",
    "*k": "Κ",
     "l": "λ",
    "*l": "Λ",
     "m": "μ",
    "*m": "Μ",
     "n": "ν",
    "*n": "Ν",
     "o": "ο",
    "*o": "Ο",
     "p": "π",
    "*p": "Π",
     "q": "θ",
    "*q": "Θ",
     "r": "ρ",
    "*r": "Ρ",
    # The decode function tentatively sets a final sigma, then patches it up to
    # be a medial sigma if it turns out to be followed by a letter.
     "s": "ς",
    "*s": "Σ",
    "s1": "σ",
    # No capital form of "s1".
    "s2": "ς",
    # No capital form of "s2".
    "s3": "ϲ",
   "*s3": "Ϲ",
     "t": "τ",
    "*t": "Τ",
     "u": "υ",
    "*u": "Υ",
     "v": "ϝ",
    "*v": "Ϝ",
     "w": "ω",
    "*w": "Ω",
     "x": "χ",
    "*x": "Χ",
     "y": "ψ",
    "*y": "Ψ",
     "z": "ζ",
    "*z": "Ζ",
}

BETA_NONLETTER_MAP = {
    ":": "·",
    "'": "’",
    "-": "‐",
    "_": "—",

     "[": "[",
     "]": "]",
    "[1": "(",
    "]1": ")",

    "\"": "\"",
}

BETA_MAP = BETA_LETTER_MAP.copy()
BETA_MAP.update(BETA_NONLETTER_MAP)

BETA_DIACRITIC_MAP = {
    ")": "\u0313", # COMBINING COMMA ABOVE
    "(": "\u0314", # COMBINING REVERSED COMMA ABOVE
    "/": "\u0301", # COMBINING ACUTE ACCENT
    "=": "\u0342", # COMBINING GREEK PERISPOMENI
   "\\": "\u0300", # COMBINING GRAVE ACCENT
    "+": "\u0308", # COMBINING DIAERESIS
    "|": "\u0345", # COMBINING GREEK YPOGEGRAMMENI
    "?": "\u0323", # COMBINING DOT BELOW
}

# https://github.com/sasansom/sedes/issues/45
#
# When we are attaching Unicode combining characters to a base character, we
# need to take care with certain diacritics so that they normalize into NFC
# nicely. The basic rule is that we want to sort these three diacritics:
#   ( ) +
# before these three:
#   / \ =
# Getting the order wrong prevents full NFC composition. For example, `i(/`,
# after decoding and normalizing, becomes the single character
#   1F35 GREEK SMALL LETTER IOTA WITH DASIA AND OXIA
# But `i/(`, if the diacritics were kept in that order, normalizes only
# partially:
#   03AF GREEK SMALL LETTER IOTA WITH TONOS
#   0314 COMBINING REVERSED COMMA ABOVE
#
# The ordering rule is a consequence of how canonical equivalence is defined for
# Greek characters (https://www.unicode.org/charts/PDF/U0370.pdf#page=2). Take
# for example 0390 GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS. 0390 is
# canonically equivalent to 03CA GREEK SMALL LETTER IOTA WITH DIALYTIKA +
# 0301 COMBINING ACUTE ACCENT. 03CA is itself canonically equivalent to
# 03B9 GREEK SMALL LETTER IOTA + 0308 COMBINING DIAERESIS.
#   0390 ≡ 03CA + 0301
#   03CA ≡ 03B9 + 0308
# Applying these equivalencies in reverse, 03B9 + 0308 + 0301 composes properly
# into 0390. But no such chain of equivalencies leads to 0390 if we start with
# the opposite order of diacritics, 03B9 + 0301 + 0308. By applying the
# canonical equivalence rule
#   03AF ≡ 03B9 + 0301
# we can get as far as 03AF GREEK SMALL LETTER IOTA WITH TONOS + 0308 COMBINING
# DIAERESIS, but from there, no further composition is possible.
#
# The order of diacritics only matters for those with the same canonical
# combining class. ( ) + / \ = all map to Unicode characters with a combining
# class of 230. The relative order of ? and | does not matter, as they map to
# characters with combining classes of 220 and 240 respectively. For
# consistency, we sort these in order of combining class, which is the same
# order that Unicode normalization would put them in.
# Unicode 3.6 P5 https://www.unicode.org/versions/Unicode13.0.0/ch03.pdf#page=42
# Unicode 3.11 D108 https://www.unicode.org/versions/Unicode13.0.0/ch03.pdf#page=66

# Diacritics in the same tier are considered incomparable. They should not
# appear attached to the same base character.
BETA_DIACRITIC_TIER = dict((c, n) for (n, tier) in enumerate((
    # Unicode combining class 220
    ("?",),
    # Unicode combining class 230
    ("(", ")", "+"),
    ("/", "\\", "="),
    # Unicode combining class 240
    ("|",),
)) for c in tier)
def cmp_diacritics(a, b):
    c = BETA_DIACRITIC_TIER[a] - BETA_DIACRITIC_TIER[b]
    if c == 0:
        raise ValueError("Cannot order diacritics {!a} and {!a}".format(a, b))
    return c
key_diacritics = functools.cmp_to_key(cmp_diacritics)
def sorted_diacritics(diacritics):
    return sorted(diacritics, key = key_diacritics)

def decode(beta):
    """Decode Beta Code to Unicode. The input Beta Code is itself a Unicode
    string; non–Beta Code code points are preserved in the result. The result is
    in NFD form."""
    STATE_INIT, STATE_LETTER_PREDIACRITICS, STATE_LETTER_DIGITS, STATE_NONLETTER_DIGITS, STATE_LETTER_POSTDIACRITICS, STATE_EMIT, STATE_DONE = range(7)

    i = 0
    def next():
        nonlocal i
        if i < len(beta):
            c = beta[i]
            i += 1
            return c
        return None

    # Beta Code lookup key of the most recently emitted character. Used to
    # resolve "s" into a medial sigma if it is followed by a letter.
    prev_key = None
    # Index of most recently emitted base character (doesn't count following
    # combining characters) in the output array. Used to resolve an already
    # emitted final sigma into a medial sigma.
    prev_basechar_index = -1

    output = []
    state = STATE_INIT
    c = next()
    while state != STATE_DONE:
        if state == STATE_INIT:
            key = ""
            diacritics = []

            if c is None:
                state = STATE_DONE
            elif c == "`":
                c = next()
            elif c == "*":
                key += "*"
                state = STATE_LETTER_PREDIACRITICS
                c = next()
            elif c.isalpha():
                key += c.lower()
                state = STATE_LETTER_DIGITS
                c = next()
            elif c in ":'-_$&^@{<>\"[]%#":
                key += c
                state = STATE_NONLETTER_DIGITS
                c = next()
            elif c in BETA_DIACRITIC_MAP:
                raise ValueError("unexpected diacritic {!r} {!r}".format(c, (beta[:i], beta[i:])))
            else:
                # Not a Beta Code sequence, some other symbol or literal code
                # point.
                prev_key = c
                prev_basechar_index = len(output)
                output.append(BETA_NONLETTER_MAP.get(c, c))
                state = STATE_INIT
                c = next()
        if state == STATE_LETTER_PREDIACRITICS:
            if c is not None and c in BETA_DIACRITIC_MAP:
                if c in diacritics:
                    raise ValueError("duplicate {!r} diacritic {!r}".format(c, (beta[:i], beta[i:])))
                diacritics.append(c)
                c = next()
            elif c is not None and c.isalpha():
                key += c.lower()
                state = STATE_LETTER_DIGITS
                c = next()
            else:
                raise ValueError("expected diacritic or alphabetic {!r}".format((beta[:i], beta[i:])))
        if state == STATE_LETTER_DIGITS:
            if c is not None and c in "0123456789":
                key += c
                c = next()
            else:
                state = STATE_LETTER_POSTDIACRITICS
        if state == STATE_NONLETTER_DIGITS:
            if c is not None and c in "0123456789":
                key += c
                c = next()
            else:
                state = STATE_EMIT
        if state == STATE_LETTER_POSTDIACRITICS:
            if c is not None and c in BETA_DIACRITIC_MAP:
                if c in diacritics:
                    raise ValueError("duplicate {!r} diacritic {!r}".format(c, (beta[:i], beta[i:])))
                diacritics.append(c)
                c = next()
            else:
                state = STATE_EMIT
        if state == STATE_EMIT:
            if prev_key == "s" and output[prev_basechar_index] == "ς" and key in BETA_LETTER_MAP:
                # Change previous character from final to medial sigma.
                output[prev_basechar_index] = "σ"
            if prev_key not in BETA_LETTER_MAP and key == "s":
                # If previous character was not a letter, this sigma must be
                # medial.
                key = "s1"
            prev_key = key
            prev_basechar_index = len(output)
            try:
                output.append(BETA_MAP[key])
            except KeyError:
                raise ValueError("unknown Beta Code character {!r} {!r}".format(key, (beta[:i], beta[i:])))
            for diacritic in sorted_diacritics(diacritics):
                output.append(BETA_DIACRITIC_MAP[diacritic])
            state = STATE_INIT

    return unicodedata.normalize("NFD", "".join(output))

# Run this module as a command to decode beta code from the command line.
# python3 betacode.py 'a)oido/s'
if __name__ == "__main__":
    import sys
    error = False
    for arg in sys.argv[1:]:
        try:
            print("{}\t{}".format(arg, decode(arg)))
        except ValueError as err:
            error = True
            print("{}\terror: {}".format(arg, err))
    if error:
        sys.exit(1)
