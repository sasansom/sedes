import copy
import unittest

import tei

class TestTokenizeText(unittest.TestCase):
    def test(self):
        WORD = tei.Token.Type.WORD
        NONWORD = tei.Token.Type.NONWORD
        for text, expected_tokens in (
            ("",
             ()),
            ("abc def,- ",
             ((WORD, "abc"), (NONWORD, " "), (WORD, "def"), (NONWORD, ",- "))),
            (" abc def,- ",
             ((NONWORD, " "),(WORD, "abc"), (NONWORD, " "), (WORD, "def"), (NONWORD, ",- "))),
            ("‘θαρσήσας μάλα εἰπὲ θεοπρόπιον ὅ τι οἶσθα:", # Il. 1.85
             ((NONWORD, "‘"), (WORD, "θαρσήσας"), (NONWORD, " "), (WORD, "μάλα"), (NONWORD, " "), (WORD, "εἰπὲ"), (NONWORD, " "), (WORD, "θεοπρόπιον"), (NONWORD, " "), (WORD, "ὅ"), (NONWORD, " "), (WORD, "τι"), (NONWORD, " "), (WORD, "οἶσθα"), (NONWORD, ":"))),
        ):
            tokens = tuple(tei.tokenize_text(text))
            self.assertEqual(tuple((token.type, token.text) for token in tokens), expected_tokens)

            line = tei.Line(tokens)
            self.assertEqual(line.text(), text)
            self.assertEqual(tuple(line.words()), tuple(text for (type, text) in expected_tokens if type == WORD))

class TestTrimTokens(unittest.TestCase):
    def test(self):
        WORD = lambda text: tei.Token(tei.Token.Type.WORD, text)
        NONWORD = lambda text: tei.Token(tei.Token.Type.NONWORD, text)
        for tokens, expected in (
            ((),
             ()),
            # only NONWORDs are trimmed
            ((WORD(" a "),),
             (WORD(" a "),)),
            ((NONWORD(" * "),),
             (NONWORD("*"),)),
            # WORDs shield inner NONWORDs
            ((NONWORD("<"), WORD("a"), NONWORD(" * "), WORD("b"), NONWORD(">")),
             (NONWORD("<"), WORD("a"), NONWORD(" * "), WORD("b"), NONWORD(">"))),
            # whitespace-only NONWORDs are removed completely
            ((NONWORD(""), NONWORD("   "), WORD("a"), NONWORD(""), NONWORD("   ")),
             (WORD("a"),)),
            ((NONWORD(""),),
             ()),
            # left side is lstripped only, right side is rstripped only
            ((NONWORD(" < "), WORD("a"), NONWORD(" > ")),
             (NONWORD("< "), WORD("a"), NONWORD(" >"))),
        ):
            tokens_copy = copy.deepcopy(tokens)
            trimmed = tuple(tei.trim_tokens(tokens_copy))
            # check output of trim_tokens
            self.assertEqual(trimmed, expected)
            # check that input is unmodified
            self.assertEqual(tokens, tokens_copy)
