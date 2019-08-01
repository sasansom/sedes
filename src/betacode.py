# coding=utf-8
#
# Beta Code decoding and encoding for Greek.
#
# http://www.stoa.org/unicode/
# http://www.tlg.uci.edu/~opoudjis/unicode/unicode.html

import unittest
import unicodedata

__all__ = ["decode"]

BETA_LETTER_MAP = {
     u"a": u"α",
    u"*a": u"Α",
     u"b": u"β",
    u"*b": u"Β",
     u"c": u"ξ",
    u"*c": u"Ξ",
     u"d": u"δ",
    u"*d": u"Δ",
     u"e": u"ε",
    u"*e": u"Ε",
     u"f": u"φ",
    u"*f": u"Φ",
     u"g": u"γ",
    u"*g": u"Γ",
     u"h": u"η",
    u"*h": u"Η",
     u"i": u"ι",
    u"*i": u"Ι",
    # Wikipedia: "Some representations use J for the final sigma..."
    # "j": u"ς",
    # No capital form of "j".
     u"k": u"κ",
    u"*k": u"Κ",
     u"l": u"λ",
    u"*l": u"Λ",
     u"m": u"μ",
    u"*m": u"Μ",
     u"n": u"ν",
    u"*n": u"Ν",
     u"o": u"ο",
    u"*o": u"Ο",
     u"p": u"π",
    u"*p": u"Π",
     u"q": u"θ",
    u"*q": u"Θ",
     u"r": u"ρ",
    u"*r": u"Ρ",
    # The decode function tentatively sets a final sigma, then patches it up to
    # be a medial sigma if it turns out to be followed by a letter.
     u"s": u"ς",
    u"*s": u"Σ",
     u"s1": u"σ",
    # No capital form of "s1".
     u"s2": u"ς",
    # No capital form of "s2".
     u"s3": u"ϲ",
    u"*s3": u"Ϲ",
     u"t": u"τ",
    u"*t": u"Τ",
     u"u": u"υ",
    u"*u": u"Υ",
     u"v": u"ϝ",
    u"*v": u"Ϝ",
     u"w": u"ω",
    u"*w": u"Ω",
     u"x": u"χ",
    u"*x": u"Χ",
     u"y": u"ψ",
    u"*y": u"Ψ",
     u"z": u"ζ",
    u"*z": u"Ζ",
}

BETA_DIACRITICAL_MAP = {
    u")": u"\u0313",
    u"(": u"\u0314",
    u"/": u"\u0301",
    u"=": u"\u0342",
    u"\\": u"\u0300",
    u"+": u"\u0308",
    u"|": u"\u0345",
    u"?": u"\u0323",
}

BETA_NONLETTER_MAP = {
    u":": u"·",
    u"'": u"’",
    u"-": u"‐",
    u"_": u"—",
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
            key = u""
            diacriticals = []

            if c is None:
                state = STATE_DONE
            elif c == u"`":
                c = next()
            elif c == u"*":
                key += u"*"
                state = STATE_PREDIACRITICALS
                c = next()
            elif c.isalpha():
                key += c.lower()
                state = STATE_DIGITS
                c = next()
            elif c in BETA_DIACRITICAL_MAP:
                raise ValueError("unexpected diacritical %r" % c)
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
                    raise ValueError(u"duplicate %r diacritical" % c)
                diacriticals.append(c)
                c = next()
            elif c is not None and c.isalpha():
                key += c.lower()
                state = STATE_DIGITS
                c = next()
            else:
                raise ValueError(u"expected diacritical or alphabetic")
        if state == STATE_DIGITS:
            if c is not None and c in u"0123456789":
                key += c
                c = next()
            else:
                state = STATE_POSTDIACRITICALS
        if state == STATE_POSTDIACRITICALS:
            if c is not None and c in BETA_DIACRITICAL_MAP:
                if c in diacriticals:
                    raise ValueError(u"duplicate %r diacritical" % c)
                diacriticals.append(c)
                c = next()
            else:
                if prev_key == u"s" and output[prev_basechar_index] == u"ς":
                    # Change previous character from final to medial sigma.
                    output[prev_basechar_index] = u"σ"
                if prev_key not in BETA_LETTER_MAP and key == u"s":
                    # If previous character was not a letter, this sigma must be
                    # medial.
                    key = u"s1"
                prev_key = key
                prev_basechar_index = len(output)
                try:
                    output.append(BETA_LETTER_MAP[key])
                except KeyError:
                    raise ValueError("unknown Beta Code letter %q" % key)
                for diacritical in diacriticals:
                    output.append(BETA_DIACRITICAL_MAP[diacritical])
                state = STATE_INIT

    return unicodedata.normalize("NFD", u"".join(output))

class TestDecode(unittest.TestCase):
    def test_letters(self):
        """Test that all single Beta Code letters decode to the correct single
        code point."""
        letters = {
             u"a": 0x03b1,
            u"*a": 0x0391,
             u"b": 0x03b2,
            u"*b": 0x0392,
             u"c": 0x03be,
            u"*c": 0x039e,
             u"d": 0x03b4,
            u"*d": 0x0394,
             u"e": 0x03b5,
            u"*e": 0x0395,
             u"f": 0x03c6,
            u"*f": 0x03a6,
             u"g": 0x03b3,
            u"*g": 0x0393,
             u"h": 0x03b7,
            u"*h": 0x0397,
             u"i": 0x03b9,
            u"*i": 0x0399,
             u"k": 0x03ba,
            u"*k": 0x039a,
             u"l": 0x03bb,
            u"*l": 0x039b,
             u"m": 0x03bc,
            u"*m": 0x039c,
             u"n": 0x03bd,
            u"*n": 0x039d,
             u"o": 0x03bf,
            u"*o": 0x039f,
             u"p": 0x03c0,
            u"*p": 0x03a0,
             u"q": 0x03b8,
            u"*q": 0x0398,
             u"r": 0x03c1,
            u"*r": 0x03a1,
             u"s": 0x03c3,
            u"*s": 0x03a3,
            u"s1": 0x03c3,
            # No capital form of "s1".
            u"s2": 0x03c2,
            # No capital form of "s2".
            u"s3": 0x03f2,
           u"*s3": 0x03f9,
             u"t": 0x03c4,
            u"*t": 0x03a4,
             u"u": 0x03c5,
            u"*u": 0x03a5,
             u"v": 0x03dd,
            u"*v": 0x03dc,
             u"w": 0x03c9,
            u"*w": 0x03a9,
             u"x": 0x03c7,
            u"*x": 0x03a7,
             u"y": 0x03c8,
            u"*y": 0x03a8,
             u"z": 0x03b6,
            u"*z": 0x0396,

             u":": 0x00b7,
             u"'": 0x2019,
             u"-": 0x2010,
             u"_": 0x2014,

            u"\n": 0x000a,
             u" ": 0x0020,
             u".": 0x002e,
             u",": 0x002c,
             u"—": 0x2014,
        }
        for beta, expected in letters.items():
            uni = decode(beta)
            self.assertEqual(len(uni), 1, u"%r returned %r" % (beta, uni))
            self.assertEqual(ord(uni), expected, u"0x%04x != 0x%04x (%r)" % (ord(uni), expected, beta))

    def test_null(self):
        """Test that the "`" character interrupts a sequence and is ignored."""
        TESTS = [
            (u"`", u""),
            (u"s`1", u"σ1"),
            (u"s1`2", u"σ2"),
        ]
        for beta, expected in TESTS:
            self.assertEqual(decode(beta), expected)
            self.assertEqual(decode(beta.upper()), expected)

    def test_words(self):
        TESTS = [
            (u"", u""),
            (u"e)gw/", u"ἐγώ"),
            (u"h(mei=s", u"ἡμεῖς"),
            (u"mousa/wn", u"μουσάων"),
            (u"*(elikwnia/dwn", u"Ἑλικωνιάδων"),
            (u"*e(likwnia/dwn", u"Ἑλικωνιάδων"),
            (u"*)odusseu/s", u"Ὀδυσσεύς"),
            (u"el/i", u"ελ́ι"), # Accent on consonant, whatever.
            # Hymn to Hermes 22–24, a pangram.
            # http://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0137:hymn=4
            (u"a)ll' o(/ g' a)nai+/cas zh/tei bo/as *)apo/llwnos ou)do\\n u(perbai/nwn u(yhrefe/os a)/ntroio. e)/nqa xe/lun eu(rw\\n e)kth/sato muri/on o)/lbon:",
             u"ἀλλ’ ὅ γ’ ἀναΐξας ζήτει βόας Ἀπόλλωνος οὐδὸν ὑπερβαίνων ὑψηρεφέος ἄντροιο. ἔνθα χέλυν εὑρὼν ἐκτήσατο μυρίον ὄλβον·"),
        ]
        for beta, expected in TESTS:
            self.assertEqual(decode(beta), expected)
            self.assertEqual(decode(beta.upper()), expected)

    def test_sigma(self):
        # http://www.tlg.uci.edu/~opoudjis/dist/sigma.html
        TESTS = [
            (u"s", u"σ"),
            (u"ss", u"σς"),
            (u"*s", u"Σ"),
            (u"s*s", u"σΣ"),
            (u"tw=| s su=s", u"τῷ σ σῦς"),
            (u"tw=| ss su=s", u"τῷ σς σῦς"),
            (u"tw=| *s su=s", u"τῷ Σ σῦς"),
            (u"tw=| s*s su=s", u"τῷ σΣ σῦς"),
            (u"stoi=xos", u"στοῖχος"),
            (u"*stoi=xos", u"Στοῖχος"),
            (u"s1toi=xos1", u"στοῖχοσ"),
            (u"s2toi=xos2", u"ςτοῖχος"),
            (u"s3toi=xos3", u"ϲτοῖχοϲ"),
            (u"*s3toi=xos3", u"Ϲτοῖχοϲ"),
        ]
        for beta, expected in TESTS:
            self.assertEqual(decode(beta), expected)
            self.assertEqual(decode(beta.upper()), expected)

    def test_invalid(self):
        TESTS = [
            u"\\e)gw/", # initial diacritical
            u"e)gw//",  # duplicate diacritical
            u"*)e)gw/", # duplicate diacritical
            u"a*",      # "*" with nothing following
            u"*`a",     # "*" with nothing following
            u"*s1",     # no capital form of "s1"
            u"*s2",     # no capital form of "s2"
        ]
        for beta in TESTS:
            try:
                uni = decode(beta)
            except ValueError:
                continue
            self.fail("%r did not raise ValueError; returned %r" % (beta, uni))

if __name__ == "__main__":
    unittest.main()
