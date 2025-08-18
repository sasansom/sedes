# Extraction of lines and limited metadata from TEI (Text Encoding Initiative)
# XML files.
# https://tei-c.org/release/doc/tei-p5-doc/en/html/index.html

import copy
import enum
import re
import sys
import xml.etree.ElementTree

# The TEI XML namespace, contained in curly brackets as conventional for xml.etree.ElementTree.
# https://tei-c.org/release/doc/tei-p5-doc/en/html/USE.html#CFNS
# https://docs.python.org/3/library/xml.etree.elementtree.html#parsing-xml-with-namespaces
NS = "{http://www.tei-c.org/ns/1.0}"

def warn(msg):
    print("warning: {}".format(msg), file=sys.stderr)

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

    def may_precede(self, other):
        """Is other a plausible line number to follow self?"""
        self_book = self.book_n
        self_number, self_extra = split_line_n(self.line_n)

        other_book = other.book_n
        other_number, other_extra = split_line_n(other.line_n)

        if self_number is None or self_book != other_book:
            # A new book means we start over at line "1" or "1a".
            # Could additionally check that other_book == self_book + 1, in the
            # case where both other_book and self_book represent integers.
            return other_number is None or (other_number == 1 and other_extra in ("", "a"))
        if self_number != other_number:
            # Within the same book, line n should be followed by line n+1 or
            # n+1"a".
            return other_number == self_number + 1 and other_extra in ("", "a")
        if self_extra == "":
            # Line n may be followed by line n"a".
            return other_extra == "a"
        return len(self_extra) == 1 and len(other_extra) == 1 and other_extra == chr(ord(self_extra) + 1)

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
        # The depth of nesting of div elements.
        # https://tei-c.org/release/doc/tei-p5-doc/en/html/DS.html#DSDIV
        self.div_depth = 0

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

def consolidate_tokens(tokens):
    """Consolidate runs of consecutive WORD and NONWORD tokens."""

    cur = None
    for token in tokens:
        if cur is not None and token.type == cur.type and token.type in (Token.Type.NONWORD, Token.Type.WORD):
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
        # function. The current line number (line_n), the previous lines @part
        # attribute (prev_part), and the partial contents of the current line
        # (partial and next_partial) are shared in common across all calls, in
        # contrast to the Environment (env), which belongs to one call. The
        # flush function is called at the end of a line to yield a line to the
        # caller.
        line_n = None
        # prev_part is the @part attribute of the previous line. It is None when
        # there is no previous line or the previous line had the attribute
        # unset. Otherwise it may have the value "I", "M", or "F" for the
        # initial, medial, or final part of a line.
        # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.fragmentable.html#tei_att.part
        prev_part = None
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
            nonlocal line_n, prev_part, partial, next_partial

            # Handle any text before the first child element.
            if root.text is not None and env.in_line:
                partial.extend(tokenize_text(root.text))

            for elem in root:
                # Make a copy of the environment to pass to recursive calls to
                # do_elem. This allows them to know, for example, what book_n
                # they're in, while enabling us to remember the environment
                # before the call.
                sub_env = env.copy()

                # Lines may be marked up in any of these ways:
                #
                #   <l n="100">first line</l>
                #   <l n="101">next line</l>
                #
                #   <lb n="100"/>first line
                #   <lb n="101"/>next line
                #
                #   <l n="100" part="I">start of first line</l>
                #   <l n="100b" part="F">end of first line</l>
                #
                #   <l n="100" part="I">start of first line</l>
                #   <l n="100b" part="M">middle of first line</l>
                #   <l n="100c" part="F">end of first line</l>
                #
                # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-l.html
                # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-lb.html
                # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.fragmentable.html#tei_att.part
                if elem.tag in (f"{NS}l", f"{NS}lb"):
                    partial.extend(next_partial)
                    next_partial.clear()

                    cur_loc = Locator(env.book_n, line_n)
                    part = elem.get("part")
                    if (part is None) or ((prev_part is None or prev_part == "F") and part == "I"):
                        # This is the beginning of a new line (the most common case).
                        # Output the previous line.
                        for x in flush(env):
                            yield x
                        # Infer a line number for the new line.
                        n = elem.get("n")
                        if n is not None:
                            # If this line has an explicit number, check it
                            # against the number of the previous line.
                            new_loc = Locator(env.book_n, n)
                            if not cur_loc.may_precede(new_loc):
                                warn("after line {!r}, expected {!r}, got {!r}".format(cur_loc, cur_loc.successor(), new_loc))
                        else:
                            # If there's no explicit number is provided, guess
                            # based on the previous line number.
                            new_loc = cur_loc.successor()
                    elif (prev_part == "I" and (part == "M" or part == "F")) or (prev_part == "M" and part == "F"):
                        # This is a continuation of the previous line. Ignore
                        # any explicit line number and reuse the previous one.
                        new_loc = cur_loc
                        # Add a space token between parts of a split line.
                        partial.append(Token(Token.Type.NONWORD, " "))
                    else:
                        raise ValueError(f"unhandled sequence of @part: {prev_part!r}, {part!r}")
                    assert env.book_n == new_loc.book_n
                    line_n = new_loc.line_n
                    prev_part = part

                    if elem.tag == f"{NS}l":
                        sub_env.in_line = True
                    elif elem.tag == f"{NS}lb":
                        env.in_line = True
                elif elem.tag == f"{NS}div":
                    # https://tei-c.org/release/doc/tei-p5-doc/en/html/DS.html#DSDIV1
                    sub_env.div_depth += 1
                    div_type = elem.get("type")
                    div_subtype = elem.get("subtype")
                    if env.div_depth == 0 and div_type in ("edition",):
                        pass
                    elif env.div_depth == 1 and div_type == "textpart" and div_subtype in ("book", "Book", "poem", "Poem"):
                        sub_env.book_n = elem.get("n")
                        # Reset the line counter at the beginning of a new book.
                        line_n = None
                    else:
                        raise ValueError(f"unknown div type={div_type!r} subtype={div_subtype!r} at nesting level {env.div_depth}")

                if elem.tag in (f"{NS}milestone", f"{NS}head", f"{NS}gap", f"{NS}pb", f"{NS}note", f"{NS}speaker"):
                    pass
                elif elem.tag in (
                    f"{NS}div",
                    f"{NS}l", f"{NS}lb", f"{NS}lg", f"{NS}p", f"{NS}sp",
                    f"{NS}add", f"{NS}del", f"{NS}name", f"{NS}supplied"
                ):
                    for x in do_elem(elem, sub_env):
                        yield x
                elif elem.tag == f"{NS}choice":
                    # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-choice.html
                    # We handle only the special case of choice containing
                    # exactly one sic and one corr element, as added here:
                    # https://github.com/PerseusDL/canonical-greekLit/commit/26023d612fffdb9ea891c723f82183a747fe2cd4#diff-ba0cff6bfc386d6392d18d1777b2b9915e93d80ed5815e4e0c29760e312dc954
                    # We ignore the sic and keep the corr.
                    if elem.text is not None:
                        raise ValueError(f"text not allowed in {elem.tag!r} element")
                    children = {}
                    for child in elem:
                        if child.tail is not None:
                            raise ValueError(f"text not allowed in {elem.tag!r} element")
                        if child.tag not in (f"{NS}sic", f"{NS}corr"):
                            raise ValueError(f"unknown child of {elem.tag!r}: {child.tag!r}")
                        if child.tag in children:
                            raise ValueError(f"duplicate child of {elem.tag!r}: {child.tag!r}")
                        children[child.tag] = child
                    corr = children.get(f"{NS}corr")
                    if corr is None:
                        raise ValueError(f"no corr child of {elem.tag!r}")
                    for x in do_elem(corr, sub_env):
                        yield x
                elif elem.tag == f"{NS}q":
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
                        for x in do_elem(elem, sub_env):
                            yield x
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
                if elem.tag == f"{NS}div" and env.div_depth == 1:
                    for x in flush(sub_env):
                        yield x
                    # At the end of a book, reset the line counter to be safe.
                    line_n = None
                    # Partial lines may not cross book boundaries.
                    if not (prev_part is None or prev_part == "F"):
                        raise ValueError(f"unfinished line at end of book: part={prev_part!r}")
                    prev_part = None

                # Handle any text between this child element and the next child
                # element, or between the end tag of this child element and the
                # end tag of the parent element.
                if elem.tail is not None and env.in_line:
                    partial.extend(tokenize_text(elem.tail))

        for x in do_elem(self.tree.find(f".//{NS}text/{NS}body"), Environment()):
            yield x
