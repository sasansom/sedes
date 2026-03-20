import copy
import io
import unittest
import xml.etree.ElementTree

import tei

class TestParser(unittest.TestCase):
    # "Make `tei.TEI` parser raise an error when XML is not well-formed"
    # https://github.com/sasansom/sedes/issues/89
    def test_non_well_formed(self):
        with self.assertRaises(xml.etree.ElementTree.ParseError):
            # Unclosed <supplied> element.
            doc = tei.TEI(io.StringIO("""\
<?xml version="1.0" encoding="utf-8"?>
<TEI.2>
<text><body>
<div1 type="Book" n="1">
<lb rend="displayNum" n="1"/>i(/ppous t' a)mfipo/leue kai\ h(mio/nous talaergou/s.
<lb/> <supplied reason="lost">w(s e)/fat': ou)rano/qen de\ path\\r *zeu\s au)to\s e)/pessi
<lb/> qh=ke te/los: pa=sin d' a)/r' o(/ g' oi)wnoi=si ke/leusen
</div1>
</body></text>
</TEI.2>
"""))
            for loc, line in doc.lines():
                pass

class TestQuotes(unittest.TestCase):
    def test(self):
        for text, expected_lines in (
            ("""\
<?xml version="1.0" encoding="utf-8"?>
<TEI.2>
<text><body>
</body></text></TEI.2>
""",
             ()),
            ("""
<TEI.2><text><body>
<div1 type="Book">
<l n="1">how now <q>brown cow</q></l>
<l n="2">it’s a <q>nested <q>quote</q></q></l>
</div1>
</body></text></TEI.2>
""",
             (
                ("1", "ηοω νοω ‘βροων ξοω’"),
                ("2", "ιτ’σ α ‘νεστεδ ‘θυοτε’’"),
             )),
            ("""
<TEI.2><text><body>
<div1 type="Book">
<lb n="1"/>how now <q>brown cow</q>
<lb n="2"/>it’s a <q>nested <q>quote</q></q>
</div1>
</body></text></TEI.2>
""",
             (
                ("1", "ηοω νοω ‘βροων ξοω’"),
                ("2", "ιτ’σ α ‘νεστεδ ‘θυοτε’’"),
             )),
            ("""
<TEI.2><text><body>
<div1 type="Book">
<lb n="1"/>how now <q>brown cow
<lb n="2"/>it’s a <q>nested</q></q> quote
</div1>
</body></text></TEI.2>
""",
             (
                ("1", "ηοω νοω ‘βροων ξοω"),
                ("2", "ιτ’σ α ‘νεστεδ’’ θυοτε"),
             )),
            ("""
<TEI.2><text><body>
<div1 type="Book">
<l n="1">quote outside</l>
<q>
<l n="2">line</l>
<l n="3">elements</l>
</q>
</div1>
</body></text></TEI.2>
""",
             (
                ("1", "θυοτε ουτσιδε"),
                ("2", "‘λινε"),
                ("3", "ελεμεντς’"),
             )),
            ("""
<TEI.2><text><body>
<div1 type="Book">
<q><l n="1"> <milestone/> text <milestone/> </l></q>
<l n="2"> <q> <milestone/> text <milestone/> </q> </l>
</div1>
</body></text></TEI.2>
""",
             (
                ("1", "‘ τεχτ’"),
                ("2", "‘ τεχτ’"),
             )),
            ("""
<TEI.2><text><body>
<div1 type="Book">
<p><lb n="1"/>quote with intervening
</p><q><p>
<lb n="2"/>paragraph
<lb n="3"/>elements
</p></q>
</div1>
</body></text></TEI.2>
""",
             (
                ("1", "θυοτε ωιτη ιντερϝενινγ"),
                ("2", "‘παραγραπη"),
                ("3", "ελεμεντς’"),
             )),
            ("""
<TEI.2><text><body>
<div1 type="Book">
<p><l n="1">quote with intervening</l>
</p><q><p>
<l n="2">paragraph</l>
<l n="3">elements</l>
</p></q>
</div1>
</body></text></TEI.2>
""",
             (
                ("1", "θυοτε ωιτη ιντερϝενινγ"),
                ("2", "‘παραγραπη"),
                ("3", "ελεμεντς’"),
             )),
        ):
            lines = tuple((str(loc), line.text()) for (loc, line) in tuple(tei.TEI(io.StringIO(text)).lines()))
            self.assertEqual(lines, expected_lines, text)

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
            # leading and trailing whitespace-only NONWORDs are removed completely
            ((NONWORD(""), NONWORD("   "), WORD("a"), NONWORD(""), NONWORD("   ")),
             (WORD("a"),)),
            ((NONWORD(""),),
             ()),
            # left side is lstripped only, right side is rstripped only
            ((NONWORD(" < "), WORD("a"), NONWORD(" > ")),
             (NONWORD("< "), WORD("a"), NONWORD(" >"))),
            # whitespace in tokens is normalized.
            ((WORD("a"), NONWORD(" \n\t   "), WORD("b")),
             (WORD("a"), NONWORD(" "), WORD("b"))),
            # WORDS and NONWORDS are consolidated
            ((NONWORD("<"), NONWORD("<"),
              WORD("a"), WORD("b"),
              NONWORD("|"),
              WORD("c"), WORD("d"),
              NONWORD(">"), NONWORD(">")),
             (NONWORD("<<"), WORD("ab"), NONWORD("|"), WORD("cd"), NONWORD(">>"))),
        ):
            tokens_copy = copy.deepcopy(tokens)
            trimmed = tuple(tei.trim_tokens(tokens_copy))
            # check output of trim_tokens
            self.assertEqual(trimmed, expected)
            # check that input is unmodified
            self.assertEqual(tokens, tokens_copy)
