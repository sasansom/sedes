# Extraction of lines and limited metadata from TEI (Text Encoding Initiative)
# XML files.
# https://tei-c.org/release/doc/tei-p5-doc/en/html/index.html

import bs4
import re
import sys

import betacode

def warn(msg):
    print("warning: {}".format(msg), file=sys.stderr)

def split_line_n(line_n):
    """Split a line number string into an (integer, everything else) pair. A
    line_n of None is treated as an empty string."""
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

        if self_book != other_book:
            # A new book means we start over at line "1" or "1a".
            # Could additionally check that other_book == self_book + 1, in the
            # case where both other_book and self_book represent integers.
            return other_number == 1 and other_extra in ("", "a")
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

class Line:
    """Line is a container for (book number, line number, text of line)."""

    def __init__(self, loc, text):
        self.book_n = loc.book_n
        self.line_n = loc.line_n
        self.text = text

    def __str__(self):
        return "{} {!r}".format(self.n, self.text)

class TEI:
    """TEI represents a TEI document read from a file stream."""

    def __init__(self, f):
        self.soup = bs4.BeautifulSoup(f, "xml")

    @property
    def title(self):
        return self.soup.teiHeader.fileDesc.titleStmt.title.get_text()

    @property
    def author(self):
        return self.soup.teiHeader.fileDesc.titleStmt.author.get_text()

    def lines(self):
        """Return an iterator over Lines extracted from the text of the TEI
        document."""

        # Internally this function works using recursion in the do_elem
        # function. The current line number (loc), and the partial contents of
        # the current line (partial) are shared in the environment common to all
        # recursive class. The flush function is called at the end of a line to
        # yield a line to the caller.
        loc = Locator()
        partial = []

        def flush():
            nonlocal loc, partial
            text = "".join(partial).strip()
            partial = []
            if text:
                yield Line(loc, text)

        def do_elem(root):
            nonlocal loc, partial
            for elem in root.children:
                if type(elem) == bs4.element.Comment:
                    pass
                elif type(elem) == bs4.element.Tag:
                    # Lines may be marked up as
                    #   <l>text text text</l>
                    #   <lb/>text text text
                    # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-l.html
                    # https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-lb.html
                    if elem.name in ("l", "lb"):
                        # Output previous line.
                        for x in flush():
                            yield x
                        n = elem.get("n")
                        if n is not None:
                            # If the new line is marked with a number, check it
                            # against the previous line.
                            new_loc = Locator(book_n=loc.book_n, line_n=n)
                            if not loc.may_precede(new_loc):
                                warn("after line {!r}, expected {!r}, got {!r}".format(loc, loc.successor(), new_loc))
                            loc = new_loc
                        else:
                            # If no line number is provided, guess based on the
                            # previous line number.
                            loc = loc.successor()
                    elif elem.name == "div1":
                        assert elem.get("type") in ("Book", "Hymn")
                        # Start counting from 1 at the beginning of a new book.
                        loc = Locator(book_n=elem.get("n"))

                    if elem.name in ("milestone", "head", "gap"):
                        pass
                    elif elem.name in ("div1", "div2", "l", "lb", "p", "q", "sp", "add", "del"):
                        for x in do_elem(elem):
                            yield x
                    else:
                        raise ValueError("don't understand element {!r}".format(elem.name))

                    if elem.name == "div1":
                        # At the end of a book, reset the counter to be safe.
                        loc = Locator()
                else:
                    partial.append(betacode.decode(elem))
            for x in flush():
                yield x

        for x in do_elem(self.soup.find("text").body):
            yield x
