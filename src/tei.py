# Extraction of lines and limited metadata from TEI (Text Encoding Initiative)
# XML files.
# https://tei-c.org/release/doc/tei-p5-doc/en/html/index.html

import copy
import enum
import re
import sys
import xml.etree.ElementTree

import betacode

def split_line_n(line_n):
    """Split a line number string into an (integer, everything else) pair. A
    line_n of None is treated as an empty string."""
    if line_n is None:
        return None, None
    m = re.match(r'^(\d*)(.*)$', line_n or "", flags=re.ASCII)
    assert m is not None, line_n
    number, extra = m.groups()
    return int(number), extra

class Locator:
    """A combination of a book (div1) number and a line number."""

    def __init__(self, book_n=None, line_n=None):
        self.book_n = book_n
        self.line_n = line_n

    def successor(self):
        """Guess a line number to follow this one. Returns a new object."""
        if self.line_n is None:
            number = ""
        else:
            m = re.match(r'^(\d*).*$', self.line_n, flags=re.ASCII)
            assert m is not None, self.line_n
            number = m.group(1)
        if not number:
            number = "0"
        number = str(int(number) + 1)
        return Locator(book_n=self.book_n, line_n=number)

    def __str__(self):
        if self.book_n is None:
            return "{}".format(self.line_n)
        else:
            return "{}.{}".format(self.book_n, self.line_n)

    def __repr__(self):
        return repr(str(self))

class Environment:
    """Environment represents the context of a call to TEI.do_elem."""

    def __init__(self):
        self.book_n = None
        self.in_line = False # Are we in a context that counts as being part of a line (i.e., not between l elements)?

    def copy(self):
        return copy.copy(self)

class Token:
    """Token represents part of a text string, distinguishing words from
    interword text and punctuation."""

    class Type(enum.Enum):
        WORD = enum.auto()
        NONWORD = enum.auto()
        OPEN_QUOTE = enum.auto()
        CLOSE_QUOTE = enum.auto()

    def __init__(self, type, text):
        self.type = type
        self.text = text

    def __eq__(self, other):
        return (self.type, self.text) == (other.type, other.text)

    def __repr__(self):
        return f"Token({self.type}, {self.text!r})"

def tokenize_text(text):
    """Split text into a sequence of WORD and NONWORD tokens."""

    prev_end = 0
    for m in re.finditer("[\\w\u0313\u0314\u0301\u0342\u0300\u0308\u0345\u0323\u2019]+", text):
        nonword = text[prev_end:m.start()]
        word = text[m.start():m.end()]
        if nonword:
            yield Token(Token.Type.NONWORD, nonword)
        if word:
            yield Token(Token.Type.WORD, word)
        prev_end = m.end()
    # Trailing nonword characters.
    nonword = text[prev_end:]
    if nonword:
        yield Token(Token.Type.NONWORD, nonword)

def tokenize_betacode(beta):
    """Decode text from beta code, then split into a sequence of WORD and
    NONWORD tokens."""
    if "?" in beta:
        raise ValueError("\"?\" not allowed in beta code; see https://github.com/sasansom/sedes/issues/11")
    return tokenize_text(betacode.decode(beta))

def consolidate_tokens(tokens):
    """Consolidate runs of consecutive WORD and NONWORD tokens."""

    cur = None
    for token in tokens:
        if cur is not None and token.type is cur.type and token.type in (Token.Type.NONWORD, Token.Type.WORD):
            cur.text += token.text
        else:
            if cur is not None:
                yield cur
            cur = copy.deepcopy(token)
    if cur is not None:
        yield cur

def trim_tokens(tokens):
    """Trim leading and trailing whitespace from a list of tokens, and
    consolidate runs of consecutive WORD and NONWORD tokens."""

    tokens = list(consolidate_tokens(tokens))
    if tokens and tokens[0].type is Token.Type.NONWORD:
        tokens[0].text = tokens[0].text.lstrip()
        if not tokens[0].text:
            tokens.pop(0)
    if tokens and tokens[-1].type is Token.Type.NONWORD:
        tokens[-1].text = tokens[-1].text.rstrip()
        if not tokens[-1].text:
            tokens.pop(-1)
    # Sometimes the source TEI has two or more spaces between words, or newlines
    # in the middle of an encoded line. Turn all those into a single space
    # character.
    for token in tokens:
        if token.type is Token.Type.NONWORD:
            token.text = re.sub(r'\s+', " ", token.text)
    return tokens

class Line:
    """Line is a sequence of tokens."""
    def __init__(self, tokens):
        self.tokens = tokens

    def text(self):
        return "".join(token.text for token in self.tokens)

    def text_without_quotes(self):
        tokens = trim_tokens([token for token in self.tokens if token.type not in (Token.Type.OPEN_QUOTE, Token.Type.CLOSE_QUOTE)])
        return "".join(token.text for token in tokens)

    def words(self):
        return (token.text for token in self.tokens if token.type == Token.Type.WORD)

class TEI:
    """TEI represents a TEI document read from a file stream."""

    def __init__(self, f):
        self.tree = xml.etree.ElementTree.parse(f)

    @property
    def title(self):
        return "".join(self.tree.find("./teiHeader/fileDesc/titleStmt/title").itertext())

    @property
    def author(self):
        return "".join(self.tree.find("./teiHeader/fileDesc/titleStmt/author").itertext())

    def lines(self):
        """Return an iterator over (Locator, str) extracted from the text of the
        TEI document."""

        # Internally this function works using recursion in the do_elem
        # function. The current line number (line_n), and the partial contents
        # of the current line (partial) are shared in common across all calls,
        # in contrast to the Environment (env), which belongs to one call. The
        # flush function is called at the end of a line to yield a line to the
        # caller.
        line_n = None
        partial = []
        # next_partial is a list of tokens to be prepended to the beginning of
        # the next line, when it starts.
        next_partial = []

        def flush(env):
            """Yield the Line represented by the current partial list and clear
            the list."""
            nonlocal line_n, partial

            if partial:
                tokens = trim_tokens(partial)
                partial.clear()
                if tokens:
                    yield Locator(env.book_n, line_n), Line(tokens)

        def do_elem(root, env):
            nonlocal line_n, partial, next_partial

            # Handle any text before the first child element.
            if root.text is not None:
                partial.extend(tokenize_betacode(root.text))

            for elem in root:
                # Make a copy of the environment to pass to recursive calls to
                # do_elem. This allows them to know, for example, what book_n
                # they're in, while enabling us to remember the environment
                # before the call.
                sub_env = env.copy()

                # Lines may be marked up as
                #   <l n="100">text text text</l>
                #   <lb n="100"/>text text text
                # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-l.html
                # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-lb.html
                if elem.tag in ("l", "lb"):
                    if elem.tag == "lb":
                        # Output the previous line. l elements are flushed
                        # at the end of the loop iteration, where the
                        # element is closed.
                        yield from flush(env)

                    partial.extend(next_partial)
                    next_partial.clear()

                    cur_loc = Locator(env.book_n, line_n)
                    n = elem.get("n")
                    if n is not None:
                        # If the new line is marked with a number, check it
                        # against the previous line.
                        new_loc = Locator(env.book_n, n)
                    else:
                        # If no line number is provided, guess based on the
                        # previous line number.
                        new_loc = cur_loc.successor()
                    assert env.book_n == new_loc.book_n
                    line_n = new_loc.line_n

                    if elem.tag == "l":
                        sub_env.in_line = True
                    elif elem.tag == "lb":
                        env.in_line = True
                elif elem.tag == "div1":
                    assert elem.get("type").lower() in ("book", "hymn", "poem"), elem.get("type")
                    sub_env.book_n = elem.get("n")
                    # Reset the line counter at the beginning of a new book.
                    line_n = None

                if elem.tag in ("milestone", "head", "gap", "pb", "note", "speaker"):
                    pass
                elif elem.tag in ("div1", "div2", "l", "lb", "p", "sp", "add", "del", "name", "supplied"):
                    yield from do_elem(elem, sub_env)
                elif elem.tag == "q":
                    # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-q.html
                    # Quotation is tricky because it can appear in two forms
                    # with essentially opposite nesting:
                    #   <lb/><q>abcd abcd abcd
                    #   <lb/>efgh efgh efgh efgh</q>
                    #
                    #   <q><l>abcd abcd abcd</l>
                    #   <l>efgh efgh efgh</l></q>
                    # The first case is easy: we just add open and close
                    # quotation marks where the open and close q tags
                    # appear. In the second case, the q element doesn't
                    # actually belong to either line; we have to migrate the
                    # open quotation mark to the beginning of the first
                    # line, and the close quotation mark to the end of the
                    # last line.
                    if env.in_line:
                        partial.append(Token(Token.Type.OPEN_QUOTE, "‘"))
                        yield from do_elem(elem, sub_env)
                        partial.append(Token(Token.Type.CLOSE_QUOTE, "’"))
                    else:
                        # Put the open quotation mark in a queue to be
                        # prepended to the next line that begins.
                        next_partial.append(Token(Token.Type.OPEN_QUOTE, "‘"))
                        # Append the close quotation mark to the final
                        # yielded line.
                        buf = None
                        for x in do_elem(elem, sub_env):
                            if buf is not None:
                                yield buf
                            buf = x
                        assert buf is not None, buf
                        loc, line = buf
                        line.tokens.append(Token(Token.Type.CLOSE_QUOTE, "’"))
                        yield loc, line
                else:
                    raise ValueError("don't understand element {!r}".format(elem.tag))

                if elem.tag == "l":
                    yield from flush(env)
                elif elem.tag == "div1":
                    yield from flush(sub_env)
                    # At the end of a book, reset the line counter to be safe.
                    line_n = None

                # Handle any text between this child element and the next child
                # element, or between the end tag of this child element and the
                # end tag of the parent element.
                if elem.tail is not None:
                    partial.extend(tokenize_betacode(elem.tail))

        yield from do_elem(self.tree.find(".//text/body"), Environment())
