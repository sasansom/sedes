# Beta Code decoding and encoding for Greek.
#
# http://www.stoa.org/unicode/
# http://www.tlg.uci.edu/encoding/quickbeta.pdf
# https://web.archive.org/web/20151104201807/http://www.tlg.uci.edu/~opoudjis/unicode/unicode.html

import unittest
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

BETA_NONLETTER_MAP = {
    ":": "·",
    "'": "’",
    "-": "‐",
    "_": "—",
}

def decode(beta):
    """Decode Beta Code to Unicode. The input Beta Code is itself a Unicode
    string; non–Beta Code code points are preserved in the result. The result is
    in NFD form."""
    STATE_INIT, STATE_PREDIACRITICALS, STATE_DIGITS, STATE_POSTDIACRITICALS, STATE_DONE = range(5)

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
                state = STATE_PREDIACRITICALS
                c = next()
            elif c.isalpha():
                key += c.lower()
                state = STATE_DIGITS
                c = next()
            elif c in BETA_DIACRITICAL_MAP:
                raise ValueError("unexpected diacritical {!r}".format(c))
            else:
                # Not an alphabetic sequence, some other symbol or literal code
                # point.
                prev_key = c
                prev_basechar_index = len(output)
                output.append(BETA_NONLETTER_MAP.get(c, c))
                state = STATE_INIT
                c = next()
        if state == STATE_PREDIACRITICALS:
            if c is not None and c in BETA_DIACRITICAL_MAP:
                if c in diacriticals:
                    raise ValueError("duplicate {!r} diacritical".format(c))
                diacriticals.append(c)
                c = next()
            elif c is not None and c.isalpha():
                key += c.lower()
                state = STATE_DIGITS
                c = next()
            else:
                raise ValueError("expected diacritical or alphabetic")
        if state == STATE_DIGITS:
            if c is not None and c in "0123456789":
                key += c
                c = next()
            else:
                state = STATE_POSTDIACRITICALS
        if state == STATE_POSTDIACRITICALS:
            if c is not None and c in BETA_DIACRITICAL_MAP:
                if c in diacriticals:
                    raise ValueError("duplicate {!r} diacritical".format(c))
                diacriticals.append(c)
                c = next()
            else:
                if prev_key == "s" and output[prev_basechar_index] == "ς":
                    # Change previous character from final to medial sigma.
                    output[prev_basechar_index] = "σ"
                if prev_key not in BETA_LETTER_MAP and key == "s":
                    # If previous character was not a letter, this sigma must be
                    # medial.
                    key = "s1"
                prev_key = key
                prev_basechar_index = len(output)
                try:
                    output.append(BETA_LETTER_MAP[key])
                except KeyError:
                    raise ValueError("unknown Beta Code letter {!r}".format(key))
                for diacritical in diacriticals:
                    output.append(BETA_DIACRITICAL_MAP[diacritical])
                state = STATE_INIT

    return unicodedata.normalize("NFD", "".join(output))

class TestDecode(unittest.TestCase):
    def test_letters(self):
        """Test that all single Beta Code letters decode to the correct single
        code point."""
        letters = {
             "a": 0x03b1,
            "*a": 0x0391,
             "b": 0x03b2,
            "*b": 0x0392,
             "c": 0x03be,
            "*c": 0x039e,
             "d": 0x03b4,
            "*d": 0x0394,
             "e": 0x03b5,
            "*e": 0x0395,
             "f": 0x03c6,
            "*f": 0x03a6,
             "g": 0x03b3,
            "*g": 0x0393,
             "h": 0x03b7,
            "*h": 0x0397,
             "i": 0x03b9,
            "*i": 0x0399,
             "k": 0x03ba,
            "*k": 0x039a,
             "l": 0x03bb,
            "*l": 0x039b,
             "m": 0x03bc,
            "*m": 0x039c,
             "n": 0x03bd,
            "*n": 0x039d,
             "o": 0x03bf,
            "*o": 0x039f,
             "p": 0x03c0,
            "*p": 0x03a0,
             "q": 0x03b8,
            "*q": 0x0398,
             "r": 0x03c1,
            "*r": 0x03a1,
             "s": 0x03c3,
            "*s": 0x03a3,
            "s1": 0x03c3,
            # No capital form of "s1".
            "s2": 0x03c2,
            # No capital form of "s2".
            "s3": 0x03f2,
           "*s3": 0x03f9,
             "t": 0x03c4,
            "*t": 0x03a4,
             "u": 0x03c5,
            "*u": 0x03a5,
             "v": 0x03dd,
            "*v": 0x03dc,
             "w": 0x03c9,
            "*w": 0x03a9,
             "x": 0x03c7,
            "*x": 0x03a7,
             "y": 0x03c8,
            "*y": 0x03a8,
             "z": 0x03b6,
            "*z": 0x0396,

             ":": 0x00b7,
             "'": 0x2019,
             "-": 0x2010,
             "_": 0x2014,

            "\n": 0x000a,
             " ": 0x0020,
             ".": 0x002e,
             ",": 0x002c,
             "—": 0x2014,
        }
        for beta, expected in letters.items():
            uni = decode(beta)
            self.assertEqual(len(uni), 1, "{!r} returned {!r}".format(beta, uni))
            self.assertEqual(ord(uni), expected, "0x{:04x} != 0x{:04x} ({!r})".format(ord(uni), expected, beta))

    def test_null(self):
        """Test that the "`" character interrupts a sequence and is ignored."""
        TESTS = [
            ("`", ""),
            ("s`1", "σ1"),
            ("s1`2", "σ2"),
        ]
        for beta, expected in TESTS:
            self.assertEqual(decode(beta), expected)
            self.assertEqual(decode(beta.upper()), expected)

    def test_words(self):
        TESTS = [
            ("", ""),
            ("e)gw/", "ἐγώ"),
            ("h(mei=s", "ἡμεῖς"),
            ("mousa/wn", "μουσάων"),
            ("*(elikwnia/dwn", "Ἑλικωνιάδων"),
            ("*e(likwnia/dwn", "Ἑλικωνιάδων"),
            ("*)odusseu/s", "Ὀδυσσεύς"),
            ("el/i", "ελ́ι"), # Accent on consonant, whatever.
            # Hymn to Hermes 22–24, a pangram.
            # http://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0137:hymn=4
            ("a)ll' o(/ g' a)nai+/cas zh/tei bo/as *)apo/llwnos ou)do\\n u(perbai/nwn u(yhrefe/os a)/ntroio. e)/nqa xe/lun eu(rw\\n e)kth/sato muri/on o)/lbon:",
             "ἀλλ’ ὅ γ’ ἀναΐξας ζήτει βόας Ἀπόλλωνος οὐδὸν ὑπερβαίνων ὑψηρεφέος ἄντροιο. ἔνθα χέλυν εὑρὼν ἐκτήσατο μυρίον ὄλβον·"),
        ]
        for beta, expected in TESTS:
            self.assertEqual(decode(beta), expected)
            self.assertEqual(decode(beta.upper()), expected)

    def test_sigma(self):
        # https://web.archive.org/web/20151112213346/http://www.tlg.uci.edu/~opoudjis/dist/sigma.html
        TESTS = [
            ("s", "σ"),
            ("ss", "σς"),
            ("*s", "Σ"),
            ("s*s", "σΣ"),
            ("tw=| s su=s", "τῷ σ σῦς"),
            ("tw=| ss su=s", "τῷ σς σῦς"),
            ("tw=| *s su=s", "τῷ Σ σῦς"),
            ("tw=| s*s su=s", "τῷ σΣ σῦς"),
            ("stoi=xos", "στοῖχος"),
            ("*stoi=xos", "Στοῖχος"),
            ("s1toi=xos1", "στοῖχοσ"),
            ("s2toi=xos2", "ςτοῖχος"),
            ("s3toi=xos3", "ϲτοῖχοϲ"),
            ("*s3toi=xos3", "Ϲτοῖχοϲ"),
        ]
        for beta, expected in TESTS:
            self.assertEqual(decode(beta), expected)
            self.assertEqual(decode(beta.upper()), expected)

    def test_invalid(self):
        TESTS = [
            "\\e)gw/", # initial diacritical
            "e)gw//",  # duplicate diacritical
            "*)e)gw/", # duplicate diacritical
            "a*",      # "*" with nothing following
            "*`a",     # "*" with nothing following
            "*s1",     # no capital form of "s1"
            "*s2",     # no capital form of "s2"
        ]
        for beta in TESTS:
            try:
                uni = decode(beta)
            except ValueError:
                continue
            self.fail("{!r} did not raise ValueError; returned {!r}".format(beta, uni))

if __name__ == "__main__":
    unittest.main()
