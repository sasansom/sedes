# coding=utf-8
#
# Beta code decoding and encoding for Greek.
#
# http://www.stoa.org/unicode/
# http://www.tlg.uci.edu/~opoudjis/unicode/unicode.html

import unittest
import unicodedata

__all__ = ["decode"]

LETTER_MAP = {
    "a": (u"α", u"Α"),
    "b": (u"β", u"Β"),
    "c": (u"ξ", u"Ξ"),
    "d": (u"δ", u"Δ"),
    "e": (u"ε", u"Ε"),
    "f": (u"φ", u"Φ"),
    "g": (u"γ", u"Γ"),
    "h": (u"η", u"Η"),
    "i": (u"ι", u"Ι"),
    # Wikipedia: "Some representations use J for the final sigma..."
    # "j": (u"σ", u"Σ"),
    "k": (u"κ", u"Κ"),
    "l": (u"λ", u"Λ"),
    "m": (u"μ", u"Μ"),
    "n": (u"ν", u"Ν"),
    "o": (u"ο", u"Ο"),
    "p": (u"π", u"Π"),
    "q": (u"θ", u"Θ"),
    "r": (u"ρ", u"Ρ"),
    "s": (u"σ", u"Σ"),
    "s1": (u"σ", None), # medial sigma
    "s2": (u"σ", None), # final sigma
    "s3": (u"σ", u"Σ"), # lunate sigma
    "t": (u"τ", u"Τ"),
    "u": (u"υ", u"Υ"),
    "v": (u"ϝ", u"Ϝ"),
    "w": (u"ω", u"Ω"),
    "x": (u"χ", u"Χ"),
    "y": (u"ψ", u"Ψ"),
    "z": (u"ζ", u"Ζ"),
}

NONLETTER_MAP = {
    " ": u" ",
    ".": u".",
    ",": u",",
    ":": u"·",
    ";": u";",
    "'": u"’",
    "-": u"‐",
    "_": u"—",
}

COMBINING_DIACRITICAL_MAP = {
    ")": u"\u0313",
    "(": u"\u0314",
    "/": u"\u0301",
    "=": u"\u0342",
    "\\": u"\u0300",
    "+": u"\u0308",
    "|": u"\u0345",
    "?": u"\u0323",
}

def decode_character(beta, i):
    upper = False
    letter = None
    diacriticals = []

    begin = i
    STATE_INIT, STATE_PREDIACRITICALS, STATE_LETTER, STATE_DIGITS, STATE_POSTDIACRITICALS, STATE_DONE = range(6)
    state = STATE_INIT
    while state != STATE_DONE:
        try:
            c = beta[i]
        except IndexError:
            c = None
        if state == STATE_INIT:
            if c in NONLETTER_MAP:
                return NONLETTER_MAP[c], i + 1
            elif c == "*":
                upper = True
                i += 1
                state = STATE_PREDIACRITICALS
                continue
            else:
                state = STATE_LETTER
                continue
        elif state == STATE_PREDIACRITICALS:
            if c in COMBINING_DIACRITICAL_MAP:
                diacriticals.append(c)
                i += 1
                continue
            else:
                state = STATE_LETTER
                continue
        elif state == STATE_LETTER:
            if c is not None and c.isalpha():
                letter = c
                i += 1
                state = STATE_DIGITS
                continue
            else:
                raise ValueError(repr(beta[begin:]))
        elif state == STATE_DIGITS:
            if c is not None and c.isdigit():
                letter += c
                i += 1
                continue
            else:
                state = STATE_POSTDIACRITICALS
                continue
        elif state == STATE_POSTDIACRITICALS:
            if c in COMBINING_DIACRITICAL_MAP:
                diacriticals.append(c)
                i += 1
                continue
            else:
                state = STATE_DONE
                continue

    u = []

    uni_lower, uni_upper = LETTER_MAP[letter.lower()]
    if upper:
        u.append(uni_upper)
    else:
        u.append(uni_lower)

    seen_diacriticals = set()
    for diacritical in diacriticals:
        if diacritical in seen_diacriticals:
            raise ValueError("duplicate diacritical %q in %q" % (diacritical, beta[begin:i]))
        seen_diacriticals.add(diacritical)
        u.append(COMBINING_DIACRITICAL_MAP[diacritical])

    return unicodedata.normalize("NFD", u"".join(u)), i

def decode(beta):
    """All forms of sigma ("s", medial "s1", final "s2", lunate "s3") become
    u"σ" or u"Σ", regardless of their position."""
    uni = []
    i = 0
    while i < len(beta):
        u, i = decode_character(beta, i)
        uni.append(u)
    return u"".join(uni)


class TestDecode(unittest.TestCase):
    def test_null(self):
        "`"

    def test_hyphen(self):
        # "2010 is the correct character for ‘hyphen’. 002D is ambiguous between ‘hyphen’ and ‘minus’ in meaning and should not be used."
        pass

    def test_letters(self):
        pass

    def test_sigma(self):
        "s, s1, s2, s3 at various positions"
        pass

    def test_words(self):
        TESTS = [
            ("mousa/wn", u"μουσάων"),
            ("*(elikwnia/dwn", u"Ἑλικωνιάδων"),
            ("*e(likwnia/dwn", u"Ἑλικωνιάδων"),
            ("*e(likwnia/dwn", u"Ἑλικωνιάδων"),
            ("*)odusseu/s", u"Ὀδυσσεύσ"),
            # Hymn to Hermes 22–24, a pangram.
            # http://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0137:hymn=4
            ("a)ll' o(/ g' a)nai+/cas zh/tei bo/as *)apo/llwnos ou)do\\n u(perbai/nwn u(yhrefe/os a)/ntroio.",
             u"ἀλλ’ ὅ γ’ ἀναΐξασ ζήτει βόασ Ἀπόλλωνοσ οὐδὸν ὑπερβαίνων ὑψηρεφέοσ ἄντροιο."),
        ]
        for beta, expected in TESTS:
            self.assertEqual(decode(beta), expected)
            self.assertEqual(decode(beta.upper()), expected)
            self.assertEqual(decode(beta.lower()), expected)

    def test_invalid(self):
        "e*l"
        pass

if __name__ == "__main__":
    unittest.main()
