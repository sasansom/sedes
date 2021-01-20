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
