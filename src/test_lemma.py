import unicodedata
import unittest

import lemma as lemma_mod

class TestLemma(unittest.TestCase):
    def test_normalization(self):
        for word, expected_lemma in (
            ("μῆνιν", "μῆνις"), # non-override
            ("βιὸν", "βιός"),   # override
        ):
            for norm in "NFC", "NFKC", "NFD", "NFKD":
                # Should be able to look up in any normalization.
                lemma = lemma_mod.lookup(unicodedata.normalize(norm, word))
                # Output should be NFD.
                self.assertEqual(lemma, unicodedata.normalize("NFD", expected_lemma))

    def test_normalization_coord(self):
        for word, expected_lemma, coord in (
            ("ἦ", "ἦ",   ("Argon.", "1", "134", "2")),
            ("ἦ", "ἠμί", ("Argon.", "1", "306", "1")),
            ("ἦ", "ἠμί", ("Argon.", 1, 306, 1)), # Should be robust to non-str coord.
        ):
            for norm in "NFC", "NFKC", "NFD", "NFKD":
                # Should be able to look up in any normalization.
                lemma = lemma_mod.lookup(unicodedata.normalize(norm, word), coord)
                # Output should be NFD.
                self.assertEqual(lemma, unicodedata.normalize("NFD", expected_lemma), (norm, word, coord))
        with self.assertRaises(KeyError):
            # Lookup by coord should raise an exception if the word at that
            # position is not as expected.
            lemma_mod.lookup("XXX", ("Argon.", "1", "306", "1"))

    def test_pre_transformations(self):
        for word, expected in (
            # Non-letters.
            ("", ("",)),
            (".", (".",)),
            ("abc", ("abc",)),
            # Single vowel, no trailing non-vowels.
            ("ἄϊδι", ("ἄϊδι",)),
            ("μηρὼ", ("μηρὼ", "μηρώ")),
            ("δαιτί", ("δαιτί", "δαιτι")),
            # Multiple vowels, no trailing non-vowels.
            ("Ζεῦ", ("Ζεῦ",)),
            ("ἀοιδοὶ", ("ἀοιδοὶ", "ἀοιδοί")),
            ("πολεμήϊα", ("πολεμήϊα", "πολεμηϊα")),
            # Single vowel with trailing non-vowels.
            ("ἀτροπος", ("ἀτροπος",)),
            ("σαρκὸς", ("σαρκὸς", "σαρκός")),
            ("φρῖσσόν", ("φρῖσσόν", "φρῖσσον")),
            # Multiple vowels with trailing non-vowels.
            ("σφεας", ("σφεας",)),
            ("ἀοιδοῖς", ("ἀοιδοῖς",)),
            ("περσεὺς", ("περσεὺς", "περσεύς")),
            ("ὑμεναίους", ("ὑμεναίους", "ὑμεναιους")),
            # Multiple diacritics, not all transformable.
            ("εἴδεΐ", ("εἴδεΐ", "εἴδεϊ"),),
            # Transformable diacritics not in final syllable.
            ("κτείνειν", ("κτείνειν",)),
            ("κοΐλην", ("κοΐλην",)),
            ("Προΐωξίς", ("Προΐωξίς", "Προΐωξις")),

            # More than one transformation possible. (Not sure if this can
            # happen with real words.)
            ("αβίὸν", ("αβίὸν", "αβίόν", "αβιὸν")),
            ("αβό̀ν", ("αβό̀ν", "αβό́ν", "αβὸν")),

            # These words have a final vowel cluster that covers more than one
            # syllable, with a transformable diacritic not on the final
            # syllable. These should really not be transformed, but the
            # transformation is probably harmless for the purpose of
            # lemmatization.
            ("ἁθρόοι", ('ἁθρόοι', 'ἁθροοι')),
            ("Ἠελίοιο", ('Ἠελίοιο', 'Ἠελιοιο')),
        ):
            word = unicodedata.normalize("NFD", word)
            expected = tuple(unicodedata.normalize("NFD", x) for x in expected)
            self.assertEqual(tuple(lemma_mod.pre_transformations(word)), expected)

            # Test upper-case variants too.
            word = word.upper()
            expected = tuple(x.upper() for x in expected)
            self.assertEqual(tuple(lemma_mod.pre_transformations(word)), expected)

        for word, expected in (
            ("ἀγαθὴν", "ἀγαθός"),
            ("τ’", "τε"),
        ):
            word = unicodedata.normalize("NFD", word)
            expected = unicodedata.normalize("NFD", expected)
            self.assertEqual(lemma_mod.lookup(word), expected)
