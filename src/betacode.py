# Beta Code decoding and encoding for Greek.
#
# http://www.stoa.org/unicode/
# http://www.tlg.uci.edu/encoding/quickbeta.pdf
# https://web.archive.org/web/20151104201807/http://www.tlg.uci.edu/~opoudjis/unicode/unicode.html

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

BETA_DIACRITICAL_MAP = {
    ")": "\u0313",
    "(": "\u0314",
    "/": "\u0301",
    "=": "\u0342",
   "\\": "\u0300",
    "+": "\u0308",
    "|": "\u0345",
    "?": "\u0323",
}

def decode(beta):
    """Decode Beta Code to Unicode. The input Beta Code is itself a Unicode
    string; non–Beta Code code points are preserved in the result. The result is
    in NFD form."""
    STATE_INIT, STATE_LETTER_PREDIACRITICALS, STATE_LETTER_DIGITS, STATE_NONLETTER_DIGITS, STATE_LETTER_POSTDIACRITICALS, STATE_EMIT, STATE_DONE = range(7)

    # Allow the next closure to modify this value.
    i = [0]
    def next():
        if i[0] < len(beta):
            c = beta[i[0]]
            i[0] += 1
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
            diacriticals = []

            if c is None:
                state = STATE_DONE
            elif c == "`":
                c = next()
            elif c == "*":
                key += "*"
                state = STATE_LETTER_PREDIACRITICALS
                c = next()
            elif c.isalpha():
                key += c.lower()
                state = STATE_LETTER_DIGITS
                c = next()
            elif c in ":'-_$&^@{<>\"[]%#":
                key += c
                state = STATE_NONLETTER_DIGITS
                c = next()
            elif c in BETA_DIACRITICAL_MAP:
                raise ValueError("unexpected diacritical {!r} {!r}".format(c, (beta[:i[0]], beta[i[0]:])))
            else:
                # Not an Beta Code sequence, some other symbol or literal code
                # point.
                prev_key = c
                prev_basechar_index = len(output)
                output.append(BETA_NONLETTER_MAP.get(c, c))
                state = STATE_INIT
                c = next()
        if state == STATE_LETTER_PREDIACRITICALS:
            if c is not None and c in BETA_DIACRITICAL_MAP:
                if c in diacriticals:
                    raise ValueError("duplicate {!r} diacritical {!r}".format(c, (beta[:i[0]], beta[i[0]:])))
                diacriticals.append(c)
                c = next()
            elif c is not None and c.isalpha():
                key += c.lower()
                state = STATE_LETTER_DIGITS
                c = next()
            else:
                raise ValueError("expected diacritical or alphabetic {!r}".format((beta[:i[0]], beta[i[0]:])))
        if state == STATE_LETTER_DIGITS:
            if c is not None and c in "0123456789":
                key += c
                c = next()
            else:
                state = STATE_LETTER_POSTDIACRITICALS
        if state == STATE_NONLETTER_DIGITS:
            if c is not None and c in "0123456789":
                key += c
                c = next()
            else:
                state = STATE_EMIT
        if state == STATE_LETTER_POSTDIACRITICALS:
            if c is not None and c in BETA_DIACRITICAL_MAP:
                if c in diacriticals:
                    raise ValueError("duplicate {!r} diacritical {!r}".format(c, (beta[:i[0]], beta[i[0]:])))
                diacriticals.append(c)
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
                raise ValueError("unknown Beta Code character {!r} {!r}".format(key, (beta[:i[0]], beta[i[0]:])))
            for diacritical in diacriticals:
                output.append(BETA_DIACRITICAL_MAP[diacritical])
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
