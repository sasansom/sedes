import unicodedata
import unittest

import betacode

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
            uni = betacode.decode(beta)
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
            self.assertEqual(betacode.decode(beta), expected)
            self.assertEqual(betacode.decode(beta.upper()), expected)

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
            self.assertEqual(betacode.decode(beta), expected)
            self.assertEqual(betacode.decode(beta.upper()), expected)

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
            ("[gai/hs]", "[γαίης]"), # nonletters should not cause medial sigma
        ]
        for beta, expected in TESTS:
            self.assertEqual(betacode.decode(beta), expected)
            self.assertEqual(betacode.decode(beta.upper()), expected)

    def test_nonletters(self):
        TESTS = [
            ("a[bg]d", "α[βγ]δ"),
            ("a[1bg]1d", "α(βγ)δ"),
            ("a\"bg\"d", "α\"βγ\"δ"),
        ]
        for beta, expected in TESTS:
            self.assertEqual(betacode.decode(beta), expected, (bytes(betacode.decode(beta), "utf-8"), bytes(expected, "utf-8")))
            self.assertEqual(betacode.decode(beta.upper()), expected)
        TESTS = [
            "a[2bg]3d", # We don't support most of the bracket codes.
            "a[12bg]12d", # "[12" should not be parsed as "[1" + "2".
        ]
        for beta in TESTS:
            try:
                uni = betacode.decode(beta)
            except ValueError:
                continue
            self.fail("{!r} did not raise ValueError; returned {!r}".format(beta, uni))

    def test_invalid(self):
        TESTS = [
            "\\e)gw/", # initial diacritic
            "e)gw//",  # duplicate diacritic
            "*)e)gw/", # duplicate diacritic
            "a*",      # "*" with nothing following
            "*`a",     # "*" with nothing following
            "*s1",     # no capital form of "s1"
            "*s2",     # no capital form of "s2"
        ]
        for beta in TESTS:
            try:
                uni = betacode.decode(beta)
            except ValueError:
                continue
            self.fail("{!r} did not raise ValueError; returned {!r}".format(beta, uni))

    def test_diacritic_ordering(self):
        """Test that the order of certain diacritics is canonicalized."""
        for beta, expected in (
            ("i(/", "\u1f35"),  # GREEK SMALL LETTER IOTA WITH DASIA AND OXIA
            ("i/(", "\u1f35"),  # GREEK SMALL LETTER IOTA WITH DASIA AND OXIA
            ("i(\\", "\u1f33"), # GREEK SMALL LETTER IOTA WITH DASIA AND VARIA
            ("i\\(", "\u1f33"), # GREEK SMALL LETTER IOTA WITH DASIA AND VARIA
            ("i(=", "\u1f37"),  # GREEK SMALL LETTER IOTA WITH DASIA AND PERISPOMENI
            ("i=(", "\u1f37"),  # GREEK SMALL LETTER IOTA WITH DASIA AND PERISPOMENI

            ("i)/", "\u1f34"),  # GREEK SMALL LETTER IOTA WITH PSILI AND OXIA
            ("i/)", "\u1f34"),  # GREEK SMALL LETTER IOTA WITH PSILI AND OXIA
            ("i)\\", "\u1f32"), # GREEK SMALL LETTER IOTA WITH PSILI AND VARIA
            ("i\\)", "\u1f32"), # GREEK SMALL LETTER IOTA WITH PSILI AND VARIA
            ("i)=", "\u1f36"),  # GREEK SMALL LETTER IOTA WITH PSILI AND PERISPOMENI
            ("i=)", "\u1f36"),  # GREEK SMALL LETTER IOTA WITH PSILI AND PERISPOMENI

            ("i+/", "\u0390"),  # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS
            ("i/+", "\u0390"),  # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS
            ("i+\\", "\u1fd2"), # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND VARIA
            ("i\\+", "\u1fd2"), # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND VARIA
            ("i+=", "\u1fd7"),  # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND PERISPOMENI
            ("i=+", "\u1fd7"),  # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND PERISPOMENI

            # Test interaction with capital letters and prediacriticals.
            ("*+i/", "\u03aa\u0301"), # GREEK CAPITAL LETTER IOTA WITH DIALYTIKA, COMBINING ACUTE ACCENT
            ("*/i+", "\u03aa\u0301"), # GREEK CAPITAL LETTER IOTA WITH DIALYTIKA, COMBINING ACUTE ACCENT
            ("*i+/", "\u03aa\u0301"), # GREEK CAPITAL LETTER IOTA WITH DIALYTIKA, COMBINING ACUTE ACCENT
            ("*i/+", "\u03aa\u0301"), # GREEK CAPITAL LETTER IOTA WITH DIALYTIKA, COMBINING ACUTE ACCENT
            ("*+/i", "\u03aa\u0301"), # GREEK CAPITAL LETTER IOTA WITH DIALYTIKA, COMBINING ACUTE ACCENT
            ("*/+i", "\u03aa\u0301"), # GREEK CAPITAL LETTER IOTA WITH DIALYTIKA, COMBINING ACUTE ACCENT
        ):
            decoded = betacode.decode(beta)
            composed = unicodedata.normalize("NFC", decoded)
            self.assertEqual(f"{composed!a}", f"{expected!a}", ", ".join(unicodedata.name(c) for c in composed))
