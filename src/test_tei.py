import copy
import io
import unittest
import xml.etree.ElementTree
import unicodedata

import tei

class TestParseRend(unittest.TestCase):
    def test(self):
        for s, expected in (
            (None, set()),
            ("merge", set(("merge",))),
            ("single merge", set(("single", "merge",))),
            ("single;merge", set(("single", "merge",))),
            ("single; merge", set(("single", "merge",))),
            (" single\n;\tmerge ", set(("single", "merge",))),
            ("merge single", set(("single", "merge",))),
            ("align(indent)", set(("align(indent)",))),
        ):
            self.assertEqual(tei.parse_rend(s), expected, s)

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

    def test_whitespace(self):
        for text, expected_lines in (
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1">test1  test1</l>
<l n="2"> test2  test2</l>
<l n="3">test3  test3 </l>
<l n="4"> test4  test4 </l>
</div>
</body></text></TEI>
""",
             (
                ("1", "test1 test1"),
                ("2", "test2 test2"),
                ("3", "test3 test3"),
                ("4", "test4 test4"),
             )),
        ):
            lines = tuple((str(loc), line.text()) for (loc, line) in tuple(tei.TEI(io.StringIO(text)).lines()))
            self.assertEqual(lines, expected_lines, text)

class TestQuotes(unittest.TestCase):
    WORD = lambda text: tei.Token(tei.Token.Type.WORD, text)
    NONWORD = lambda text: tei.Token(tei.Token.Type.NONWORD, text)
    OPEN_QUOTE = tei.Token(tei.Token.Type.OPEN_QUOTE, "‘")
    CLOSE_QUOTE = tei.Token(tei.Token.Type.CLOSE_QUOTE, "’")

    def test(self):
        for text, expected_lines in (
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
</body></text></TEI>
""",
             ()),
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1">how now <q>brown cow</q></l>
<l n="2">it’s a <q>nested <q>quote</q></q></l>
</div>
</body></text></TEI>
""",
             (
                ("1", "how now ‘brown cow’"),
                ("2", "it’s a ‘nested ‘quote’’"),
             )),
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<lb n="1"/>how now <q>brown cow</q>
<lb n="2"/>it’s a <q>nested <q>quote</q></q>
</div>
</body></text></TEI>
""",
             (
                ("1", "how now ‘brown cow’"),
                ("2", "it’s a ‘nested ‘quote’’"),
             )),
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<lb n="1"/>how now <q>brown cow
<lb n="2"/>it’s a <q>nested</q></q> quote
</div>
</body></text></TEI>
""",
             (
                ("1", "how now ‘brown cow"),
                ("2", "it’s a ‘nested’’ quote"),
             )),
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1">quote outside</l>
<q>
<l n="2">line</l>
<l n="3">elements</l>
</q>
</div>
</body></text></TEI>
""",
             (
                ("1", "quote outside"),
                ("2", "‘line"),
                ("3", "elements’"),
             )),
        ):
            lines = tuple((str(loc), line.text()) for (loc, line) in tuple(tei.TEI(io.StringIO(text)).lines()))
            self.assertEqual(lines, expected_lines, text)

    def test_merge(self):
        for text, expected_lines in (
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1"><q>hello</q><q rend="merge">world</q></l>
</div>
</body></text></TEI>
""",
             (
                ("1", "‘helloworld’"),
             )),
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1">Juliet asked <q>O Romeo, Romeo,</q></l>
<l n="2"><q rend="merge">wherefore art thou</q></l>
<l n="3"><q rend="merge">Romeo?</q> Exeunt.</l>
<l n="4">Merge across <q>nested <q>quotes</q></q></l>
<l n="5"><q rend="merge"><q rend="merge">that are nested.</q></q></l>
<l n="6">Merge just <q>the <q>outer</q></q></l>
<l n="7"><q rend="merge"><q>quote</q></q> this time.</l>
<l n="8"><q>But don't merge</q> this one.</l>
</div>
</body></text></TEI>
""",
             (
                ("1", "Juliet asked ‘O Romeo, Romeo,"),
                ("2", "wherefore art thou"),
                ("3", "Romeo?’ Exeunt."),
                ("4", "Merge across ‘nested ‘quotes"),
                ("5", "that are nested.’’"),
                ("6", "Merge just ‘the ‘outer’"),
                ("7", "‘quote’’ this time."),
                ("8", "‘But don't merge’ this one."),
             )),
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<q>
<l n="1">block</l>
<l n="2">quote</l>
</q>
<l n="3"><q rend="merge">merge it</q></l>
</div>
</body></text></TEI>
""",
             (
                ("1", "‘block"),
                ("2", "quote"),
                ("3", "merge it’"),
             )),
            # Test rend with other things mixed in besides "merge".
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1"><q rend="single">Hello</q></l>
<l n="2"><q rend="merge; single">world</q></l>
<l n="3"><q rend="single">Hello</q></l>
<l n="4"><q rend="single; merge">world</q></l>
<l n="5"><q rend="single">Hello</q></l>
<l n="6"><q rend="   merge  ;  single  ">world</q></l>
<l n="7"><q rend="double">Hello</q></l>
<l n="8"><q rend="double; merge">world</q></l>
<l n="9"><q rend="single">Hello</q></l>
<l n="10"><q rend="double; merge">world</q></l>
</div>
</body></text></TEI>
""",
             (
                ("1", "‘Hello"),
                ("2", "world’"),
                ("3", "‘Hello"),
                ("4", "world’"),
                ("5", "‘Hello"),
                ("6", "world’"),
                ("7", "‘Hello"),
                ("8", "world’"),
                ("9", "‘Hello"),
                ("10", "world’"),
             )),
            # Whitespace at the beginning or end of certain elements does not
            # prevent merging.
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1"><q>hello</q> </l>
<l n="2"> <q rend="merge">world</q> </l>
</div>
</body></text></TEI>
""",
             (
                ("1", "‘hello"),
                ("2", "world’"),
             )),
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1"><q>hello <q>world</q> </q> </l>
<l n="2"><q rend="merge">!!!</q></l>
</div>
</body></text></TEI>
""",
             (
                ("1", "‘hello ‘world’"),
                ("2", "!!!’"),
             )),
        ):
            lines = tuple((str(loc), line.text()) for (loc, line) in tuple(tei.TEI(io.StringIO(text)).lines()))
            self.assertEqual(lines, expected_lines, text)

    def test_merge_bad(self):
        for text in (
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1"><q rend="merge">hello</q></l>
</div>
</body></text></TEI>
""",
            # Text, even whitespace, between q elements prevents merging.
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1"><q>hello</q> <q rend="merge">world</q></l>
</div>
</body></text></TEI>
""",
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1"><q>hello</q> X</l>
<l n="2"><q rend="merge">world</q></l>
</div>
</body></text></TEI>
""",
        ):
            with self.assertRaises(ValueError, msg = text):
                tuple(tei.TEI(io.StringIO(text)).lines())

class TestFragments(unittest.TestCase):
    def test_good(self):
        WORD = lambda text: tei.Token(tei.Token.Type.WORD, text)
        NONWORD = lambda text: tei.Token(tei.Token.Type.NONWORD, text)
        OPEN_QUOTE = tei.Token(tei.Token.Type.OPEN_QUOTE, "‘")
        CLOSE_QUOTE = tei.Token(tei.Token.Type.CLOSE_QUOTE, "’")
        for text, expected_lines in (
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1">first line</l>
<l n="2">second line</l>
</div>
</body></text></TEI>
""",
             (
                ("1", "first line"),
                ("2", "second line"),
             )),
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1" part="I">start of line</l>
<l n="1b" part="F">end of line</l>
<l n="2">new line</l>
</div>
</body></text></TEI>
""",
             (
                ("1", "start of line end of line"),
                ("2", "new line"),
             )),
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1" part="I">start of line</l>
<l n="1b" part="M">middle of line</l>
<l n="1c" part="F">end of line</l>
<l n="2">new line</l>
</div>
</body></text></TEI>
""",
             (
                ("1", "start of line middle of line end of line"),
                ("2", "new line"),
             )),
            ("""
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1" part="I">a</l>
<l n="1b" part="M">b</l>
<l n="1c" part="M">c</l>
<l n="1d" part="F">d</l>
<l n="2">new line</l>
</div>
</body></text></TEI>
""",
             (
                ("1", "a b c d"),
                ("2", "new line"),
             )),
        ):
            lines = tuple((str(loc), line.text()) for (loc, line) in tuple(tei.TEI(io.StringIO(text)).lines()))
            self.assertEqual(lines, expected_lines, text)

    def test_bad(self):
        for text in (
            # F with no preceding I.
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1">first line</l>
<l n="2b" part="F">end of line</l>
</div>
</body></text></TEI>
""",
            # M with no preceding I.
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1">first line</l>
<l n="2b" part="M">middle of line</l>
<l n="2c" part="F">end of line</l>
</div>
</body></text></TEI>
""",
            # I with no M or F.
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1" part="I">start of line</l>
</div>
</body></text></TEI>
""",
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1" part="I">start of line</l>
<l n="2">new line</l>
</div>
</body></text></TEI>
""",
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<div type="textpart" subtype="book" n="1">
<l n="1" part="I">start of line</l>
</div>
<div type="textpart" subtype="book" n="2">
<l n="1">new book</l>
</div>
</div>
</body></text></TEI>
""",
            # I, M with no F.
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1" part="I">start of line</l>
<l n="1b" part="M">middle of line</l>
</div>
</body></text></TEI>
""",
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<l n="1" part="I">start of line</l>
<l n="1b" part="M">middle of line</l>
<l n="2">new line</l>
</div>
</body></text></TEI>
""",
            """
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
<div type="textpart" subtype="book" n="1">
<l n="1" part="I">start of line</l>
<l n="1b" part="M">middle of line</l>
</div>
<div type="textpart" subtype="book" n="2">
<l n="1">new book</l>
</div>
</div>
</body></text></TEI>
""",
        ):
            with self.assertRaises(ValueError, msg = text):
                tuple(tei.TEI(io.StringIO(text)).lines())

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
            tokens = tuple((token.type, token.text) for token in tei.tokenize_text(text))
            expected_tokens = tuple((type, unicodedata.normalize("NFD", text)) for (type, text) in expected_tokens)
            self.assertEqual(tokens, expected_tokens, text)

            line = tei.Line(tuple(tei.tokenize_text(text)))
            self.assertEqual(line.text(), unicodedata.normalize("NFD", text), text)
            self.assertEqual(tuple(line.words()), tuple(text for (type, text) in expected_tokens if type == WORD), text)

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
            self.assertEqual(trimmed, expected, tokens)
            # check that input is unmodified
            self.assertEqual(tokens, tokens_copy, tokens)
