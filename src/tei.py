# Extraction of lines and limited metadata from TEI (Text Encoding Initiative)
# XML files.
# https://tei-c.org/release/doc/tei-p5-doc/en/html/index.html

import enum
import re
import sys
import xml.etree.ElementTree
import unicodedata

# The TEI XML namespace, contained in curly brackets as conventional for xml.etree.ElementTree.
# https://tei-c.org/release/doc/tei-p5-doc/en/html/USE.html#CFNS
# https://docs.python.org/3/library/xml.etree.elementtree.html#parsing-xml-with-namespaces
NS = "{http://www.tei-c.org/ns/1.0}"

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
    """A combination of a book number (attribute @n in <div type="textpart" subtype="book" n="...">)
    and a line number (attribute @n in <l n="...">)."""

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

# Parse a @rend attribute. The return value is a set which contains all the
# tokens included in the attribute. According to the TEI specification, the
# delimiter between tokens is whitespace only; but Perseus texts use whitespace
# and a semicolon.
# https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.global.rendition.html#tei_att.rend
# "The values of the rend attribute are a set of sequence-indeterminate
# individual tokens separated by whitespace."
# https://tei-c.org/release/doc/tei-p5-doc/en/html/ST.html#STGAre
# "The @rend attribute values are sequence-indeterminate set of
# whitespace-separated tokens."
def parse_rend(s):
    if s is None:
        return set()
    else:
        return set(re.findall(r'[^\s;]+', s))

# Extracting metrically isolated lines of text from a TEI document is tricky in
# the general case, because the divisions in the XML structure of TEI do not
# always correspond to the line divisions we want. The main difficulties have to
# do with metrical lines divided across typographic lines, and with quotations.
# (Which are both instances of overlapping hierarchies.)
#
# Lines may be delimited by l or lb elements. l *encloses* lines, while lb
# ("line beginning") *separates* lines.
# https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-l.html
# https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-lb.html
# Perseus 6 mostly prefers l over lb, but we understand both.
#
#   <l n="1">first line</l>
#   <l n="2">second line</l>
#
#   <lb n="1"/>first line
#   <lb n="2"/>second line
#
# One line at the metrical level may be made up of multiple lines at the TEI
# level. This is indicated by the @part attribute.
# https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.fragmentable.html#tei_att.part
# An unset @part indicates a complete line. Otherwise, @part may be "I"
# (initial), "M" (medial), or "F" (final). There may be one "I" part, followed
# by any number of "M" parts, followed by one "F" part. @part only works with
# the l element, not lb.
#
#   <l n="1" part="I">complete first line</l>
#   <l n="2" part="I">initial part of second line</l>
#   <l n="2b" part="F">final part of second line</l>
#   <l n="3" part="I">initial part of third line</l>
#   <l n="3b" part="M">medial part of third line</l>
#   <l n="3c" part="F">final part of third line</l>
#
# Lines may be interleaved with quotations (q elements) in various ways. The
# simplest case is when a quotation is contained entirely within a single line
# (no difficulties with overlapping hierarchies in this case):
#
#   <l n="1">Say <q>goodnight</q>, Gracie</l>
#
#   <lb n="1"/>Say <q>goodnight</q>, Gracie
#
# A q element may *enclose* multiple while lines. When this happens, we
# interpret it as if there where an opening quotation mark at the beginning of
# the first enclosed line, and a closing quotation mark at the end of the final
# enclosed line.
#
#   <l n="1">The priestess of Mercury intones:</l>
#   <q>
#   <l n="2">Pilgrim, you enter</l>
#   <l n="3">a sacred place!</l>
#   </q>
#   <l n="4">You experience a sense of peace.</l>
#
# With lb elements, q elements may span multiple lines and may begin and end at
# the beginning, end, or middle of lines:
#
#   <lb n="1"/>She said: <q>I think
#   <lb n="2"/>that you should leave</q>
#   <lb n="3"/>before long.</q><q>Only
#   <lb n="4"/>too gladly</q> was the other's reply.

# To cope with these challenges, we parse TEI in multiple layers. The lowest
# layer, the events function below, digests the hierarchical XML structure and
# decomposes it into a nonhierarchical sequence of "events", represented by the
# Event type (which is internal to this module). Events are things like
# LINE_BEGIN and LINE_END, QUOTE_BEGIN and QUOTE_END. At this layer, the events
# are not necessarily interleaved semantically they way we want them: for
# example, <q><l></l><l></l></q> will have the QUOTE_BEGIN and QUOTE_END events
# entirely outside the LINE_BEGIN and LINE_END events. Partial lines are not
# joined but are represented by multiple LINE_BEGIN/LINE_END pairs.
#
# The next layer up is the filter_events function. This function consumes the
# low-level sequence of events and makes local adjustments to make the sequence
# more amenable to interpretation. It pushes QUOTE_BEGIN and QUOTE_END "inside"
# the lines they belong to, joins partial lines, and merges quotations.
#
# The top layer is TEI.lines, which consumes the processed sequence of events
# from filter_events. Comparatively little processing is required at this layer,
# mostly just bundling up text between successive LINE_BEGIN and LINE_END
# events.

# The meaning of the data field depends on the event type:
# BOOK_BEGIN: book number (as a string)
# BOOK_END: not allowed
# LINE_BEGIN: (line_n, line_part), where line_n is a string or None and line_part is "I", "M", "F", or None
# LINE_END: not allowed
# QUOTE_BEGIN: boolean indicating rend="merge" or not
# QUOTE_END: not allowed
# TEXT: text content
class Event:
    class Type(enum.Enum):
        BOOK_BEGIN = enum.auto()
        BOOK_END = enum.auto()
        LINE_BEGIN = enum.auto()
        LINE_END = enum.auto()
        QUOTE_BEGIN = enum.auto()
        QUOTE_END = enum.auto()
        TEXT = enum.auto()

    def __init__(self, type, data = None):
        self.type = type
        if type in (Event.Type.BOOK_END, Event.Type.LINE_END, Event.Type.QUOTE_END,):
            assert data is None, (type, data)
        self.data = data

    def __repr__(self):
        if self.data is None:
            return f"Event({self.type})"
        else:
            return f"Event({self.type}, {self.data!r}))"

# Elements that should have whitespace trimmed from the beginning and end of
# their contents. Perseus texts often have whitespace at the ends of lines,
# especially. We don't want it in any case, but if not removed, it causes
# problems with quotation merging in cases like this:
#   <l><q>hello there</q> </l>
#   <l><q rend="merge">world</q>.</l>
# The space at the end of the first line looks like content between the
# quotations, which causes an error when the <q rend="merge"> sees it's not
# immediately adjacent to a preceding </q>.
TRIM_WHITESPACE_ELEMENTS = set((f"{NS}l", f"{NS}q"))

# Generate a sequence of raw Events from a TEI element. div_depth is the number
# of div elements that are ancestors of elem. in_line indicates whether the
# given elem is inside a line (within <l></l> or after <lb/>).
def events(elem, div_depth, in_line):
    # Count the child elements of elem because there's special handling of
    # child.tail in the final child element only.
    num_children = sum(1 for _ in elem)
    for (n, child) in enumerate(elem):
        if child.tag == f"{NS}div":
            # https://tei-c.org/release/doc/tei-p5-doc/en/html/DS.html#DSDIV1
            div_type = child.get("type")
            div_subtype = child.get("subtype")
            if div_depth == 0 and div_type in ("edition",):
                pass
            elif div_depth == 1 and div_type == "textpart" and div_subtype in ("book", "Book", "poem", "Poem"):
                yield Event(Event.Type.BOOK_BEGIN, child.get("n"))
            elif div_depth >= 1 and div_type == "textpart" and div_subtype is None:
                # Hom.Hymn 3 uses <div type="textpart"> with no subtype
                # to separate the Delian and Pythian parts.
                # https://github.com/PerseusDL/canonical-greekLit/blob/2f26022a1c47089e6469b44d78f14b94aedc447d/data/tlg0013/tlg003/tlg0013.tlg003.perseus-grc2.xml#L85
                # https://github.com/PerseusDL/canonical-greekLit/blob/2f26022a1c47089e6469b44d78f14b94aedc447d/data/tlg0013/tlg003/tlg0013.tlg003.perseus-grc2.xml#L85
                pass
            else:
                raise ValueError(f"unknown div type={div_type!r} subtype={div_subtype!r} at nesting level {div_depth}")
            div_depth += 1
        elif child.tag == f"{NS}l":
            # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-l.html
            if in_line:
                raise ValueError(f"{child.tag} element while already in a line")
            in_line = True
            yield Event(Event.Type.LINE_BEGIN, (child.get("n"), child.get("part")))
        elif child.tag == f"{NS}lb":
            # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-lb.html
            if in_line:
                yield Event(Event.Type.LINE_END)
            in_line = True
            if child.get("part") is not None:
                raise ValueError(f"the part attribute is not allowed on the lb element")
            yield Event(Event.Type.LINE_BEGIN, (child.get("n"), None))
        elif child.tag == f"{NS}q":
            # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-q.html
            # Set a flag if the q element's @rend attribute contains the token
            # "merge". Perseus uses this token to indicate that this quotation
            # should be merged with one that was enclosed in a preceding
            # element.
            merge = "merge" in parse_rend(child.get("rend"))
            yield Event(Event.Type.QUOTE_BEGIN, merge)

        if (
            child.tag in (f"{NS}milestone", f"{NS}head", f"{NS}gap", f"{NS}pb", f"{NS}note", f"{NS}speaker")
            # nonnusdionysiaca.xml uses <l rend="argument"> for per-book headings.
            # https://github.com/sasansom/sedes/issues/57#issuecomment-3348714105
            or (child.tag == f"{NS}l" and "argument" in parse_rend(child.get("rend")))
        ):
            # Ignore the contents of these elements.
            pass
        elif child.tag in (
            f"{NS}div",
            f"{NS}l", f"{NS}lb", f"{NS}lg", f"{NS}p", f"{NS}sp",
            f"{NS}q",
            f"{NS}add", f"{NS}del", f"{NS}name", f"{NS}supplied", f"{NS}surplus", f"{NS}sic",
        ):
            # Handle any text after the start tag, preceding the first child
            # element. If we're in a line, yield a TEXT event. Outside a line,
            # ignore whitespace and raise an error for any non-whitespace.
            if in_line:
                text = child.text
                if text is not None and child.tag in TRIM_WHITESPACE_ELEMENTS:
                    # child is an element that should have whitespace trimmed.
                    # Trim the left side of child.text.
                    text = text.lstrip()
                    # If child has no subelements of its own, only text, then we
                    # must also trim the right side of child.text.
                    num_grandchildren = sum(1 for _ in child)
                    if num_grandchildren == 0:
                        text = text.rstrip()
                if text:
                    yield Event(Event.Type.TEXT, text)
            elif not (child.text is None or child.text.strip() == ""):
                raise ValueError(f"non-whitespace text outside line: {child.text!r}")

            # Recurse into the children of this element.
            yield from events(child, div_depth, in_line)
        else:
            raise ValueError(f"don't understand element {child.tag!r}")

        if child.tag == f"{NS}div":
            div_depth -= 1
            if div_depth == 1 and div_type == "textpart" and div_subtype in ("book", "Book", "poem", "Poem"):
                yield Event(Event.Type.BOOK_END)
        elif child.tag == f"{NS}l":
            assert in_line
            in_line = False
            yield Event(Event.Type.LINE_END)
        elif child.tag == f"{NS}lb":
            pass
        elif child.tag == f"{NS}q":
            yield Event(Event.Type.QUOTE_END)

        # Handle any text after the end tag. If we're in a line, yield a TEXT
        # event. Outside a line, ignore whitespace and raise an error for any
        # non-whitespace.
        if in_line:
            tail = child.tail
            if tail is not None and elem.tag in TRIM_WHITESPACE_ELEMENTS:
                # elem is an element that should have whitespace trimmed. If
                # we're looking at its final child, trim the right side of
                # child.tail. Note that we check *elem*.tag but modify
                # *child*.tail. Unlike child.text, child.tail is *outside* the
                # tags of child: it belongs to the parent element; i.e., elem.
                if n == num_children - 1:
                    tail = tail.rstrip()
            if tail:
                yield Event(Event.Type.TEXT, tail)
        elif not (child.tail is None or child.tail.strip() == ""):
            raise ValueError(f"non-whitespace text outside line: {child.tail!r}")

def filter_events(events):
    # An adjusted iterator over events that lets you defer events until after
    # the next LINE_BEGIN event by appending them to after_next_line_begin.
    after_next_line_begin = []
    def deferred(events):
        for event in events:
            yield event
            if event.type == Event.Type.LINE_BEGIN:
                for event in after_next_line_begin:
                    yield event
                after_next_line_begin.clear()
    # A buffer of events that have not been output yet.
    buf = []
    # Whether we are currently in a line.
    in_line = False
    # prev_line_part is the @part attribute of the previous line. It is None
    # when there is no previous line yet, or when the previous line had the
    # attribute unset. Otherwise it may have the value "I", "M", or "F" for the
    # initial, medial, or final part of a line.
    # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.fragmentable.html#tei_att.part
    # When prev_line_part is not None, it means the previous line was incomplete
    # and will be extended by the current line.
    prev_line_part = None
    # The index in buf of the most recent LINE_END event, set whenever we may
    # still need to insert a QUOTE_BEGIN event before the end of the line.
    most_recent_line_end = None
    # A QUOTE_END inserted into buf may get canceled by a later QUOTE_BEGIN that
    # requests merging. We track a stack of QUOTE_END elements, clearing the
    # stack whenever something intervenes that would make merging impossible,
    # like unquoted text or a book boundary. LINE_BEGIN and LINE_END do not
    # prevent merging.
    unresolved_quote_ends = []
    for event in deferred(events):
        if event.type == Event.Type.BOOK_BEGIN:
            in_line = False
            assert not buf, buf
            assert prev_line_part is None, prev_line_part
            assert not unresolved_quote_ends, unresolved_quote_ends
            most_recent_line_end = None
            buf.append(event)
        elif event.type == Event.Type.BOOK_END:
            in_line = False
            if not (prev_line_part is None or prev_line_part == "F"):
                raise ValueError(f"unfinished line part at BOOK_END: part={prev_line_part!r}")
            prev_line_part = None
            most_recent_line_end = None
            # Quotations cannot merge across book boundaries.
            unresolved_quote_ends.clear()
            buf.append(event)
        elif event.type == Event.Type.LINE_BEGIN:
            assert not in_line, event
            in_line = True

            line_n, line_part = event.data
            if (prev_line_part is None or prev_line_part == "F") and (line_part is None or line_part == "I"):
                # This is the the beginning of a new line (the usual case).
                # Remove the line_part from the event, because it is needed only
                # by this processing layer.
                buf.append(Event(Event.Type.LINE_BEGIN, (line_n, None)))
            elif ((prev_line_part == "I" and (line_part == "M" or line_part == "F")) or
                  (prev_line_part == "M" and (line_part == "M" or line_part == "F"))):
                # This is a continuation of the previous line. Throw away this
                # LINE_BEGIN event (and its line number) and replace the earlier
                # LINE_END with a space.
                buf[most_recent_line_end] = Event(Event.Type.TEXT, " ")
            else:
                raise ValueError(f"unhandled sequence of @part: {prev_line_part!r}, {line_part!r}")
            prev_line_part = line_part

            most_recent_line_end = None
            # LINE_BEGIN and LINE_END do not affect unresolved_quote_ends.
        elif event.type == Event.Type.LINE_END:
            assert in_line, event
            in_line = False
            most_recent_line_end = len(buf)
            # LINE_BEGIN and LINE_END do not affect unresolved_quote_ends.
            buf.append(event)
        elif event.type == Event.Type.QUOTE_BEGIN:
            merge = event.data
            if merge:
                # Cancel the most recent QUOTE_END and throw away this QUOTE_BEGIN.
                assert most_recent_line_end is None, most_recent_line_end
                try:
                    unresolved_quote_end = unresolved_quote_ends.pop()
                except IndexError:
                    raise ValueError("<q rend=\"merge\"> without a preceding </q>")
                buf.pop(unresolved_quote_end)
            else:
                # A non-merge QUOTE_BEGIN resolves all outstanding QUOTE_END.
                unresolved_quote_ends.clear()
                if in_line:
                    # Add this QUOTE_BEGIN to the events of this line.
                    buf.append(event)
                else:
                    # We're not currently in a line; save this QUOTE_BEGIN to go
                    # after the next LINE_BEGIN.
                    after_next_line_begin.append(event)
        elif event.type == Event.Type.QUOTE_END:
            if in_line:
                # We may end up canceling this QUOTE_END, if there's a future
                # "merge" QUOTE_BEGIN.
                unresolved_quote_ends.append(len(buf))
                # Add this QUOTE_END to the events of this line.
                buf.append(event)
            else:
                # We're not currently in a line; insert this QUOTE_END at the
                # end of the most recent line.
                assert most_recent_line_end is not None
                # Likewise, we may end up canceling this QUOTE_END later.
                unresolved_quote_ends.append(most_recent_line_end)
                buf.insert(most_recent_line_end, event)
                most_recent_line_end += 1
        elif event.type == Event.Type.TEXT:
            assert in_line, event
            # Any text between quotes resolves all outstanding QUOTE_END.
            unresolved_quote_ends.clear()
            # Add this TEXT event to the current line.
            buf.append(event)
        else:
            raise ValueError(event.type)
        # If prev_line_part and most_recent_line_end are unset, and
        # unresolved_quote_ends is empty, there is nothing in buf that we may
        # have to adjust. Flush it all to the output.
        if (
            prev_line_part is None and
            most_recent_line_end is None and
            not unresolved_quote_ends
        ):
            for event in buf:
                yield event
            buf.clear()
    for event in buf:
        yield event
    # The final line may have been a <lb/> without a LINE_END event. Add a
    # LINE_END if so.
    if in_line:
        in_line = False
        yield Event(Event.Type.LINE_END)
    if not (prev_line_part is None or prev_line_part == "F"):
        raise ValueError(f"unfinished line part at BOOK_END: part={prev_line_part!r}")

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

    text = unicodedata.normalize("NFD", text)

    # Normalize quotation marks. Perseus texts often use U+02BC MODIFIER LETTER
    # APOSTROPHE as an apostrophe, rather than U+2019 RIGHT SINGLE QUOTATION MARK:
    # https://github.com/sasansom/sedes/issues/57#issuecomment-830509464
    # The use of U+02BC for right-quote is by design. The presence of its
    # left-quote counterpart U+02BD MODIFIER LETTER REVERSED COMMA, however, is
    # an error: that only appears in contexts where text quotation marks should
    # be replace with <q> elements, or in other erroneous contexts.
    assert "\u02bd" not in text, text
    text = text.replace("\u02bc", "\u2019")

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
        if cur is not None and token.type is cur.type and token.type in (Token.Type.NONWORD, Token.Type.WORD):
            cur.text += token.text
        else:
            if cur is not None:
                yield cur
            cur = Token(token.type, token.text)
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
        return "".join(self.tree.find(f"./{NS}teiHeader/{NS}fileDesc/{NS}titleStmt/{NS}title").itertext())

    @property
    def author(self):
        return "".join(self.tree.find(f"./{NS}teiHeader/{NS}fileDesc/{NS}titleStmt/{NS}author").itertext())

    def lines(self):
        """Return an iterator over (Locator, str) extracted from the text of the
        TEI document."""

        cur_loc = Locator(None, None)
        tokens = []

        for event in filter_events(events(self.tree.find(f".//{NS}text/{NS}body"), 0, False)):
            if event.type == Event.Type.BOOK_BEGIN:
                book_n = event.data
                cur_loc = Locator(book_n, None)
            elif event.type == Event.Type.BOOK_END:
                cur_loc = Locator(None, None)
            elif event.type == Event.Type.LINE_BEGIN:
                assert not tokens, tokens
                line_n, _ = event.data
                if line_n is not None:
                    # If this line has an explicit number, use it.
                    new_loc = Locator(cur_loc.book_n, line_n)
                else:
                    # If there's no explicit line number, guess based on the
                    # previous line number.
                    new_loc = cur_loc.successor()
                cur_loc = new_loc
            elif event.type == Event.Type.LINE_END:
                yield cur_loc, Line(trim_tokens(tokens))
                tokens.clear()
            elif event.type == Event.Type.QUOTE_BEGIN:
                tokens.append(Token(Token.Type.OPEN_QUOTE, "‘"))
            elif event.type == Event.Type.QUOTE_END:
                tokens.append(Token(Token.Type.CLOSE_QUOTE, "’"))
            elif event.type == Event.Type.TEXT:
                tokens.extend(tokenize_text(event.data))

        assert not tokens, tokens
