# Extraction of lines and limited metadata from TEI (Text Encoding Initiative)
# XML files.
# https://tei-c.org/release/doc/tei-p5-doc/en/html/index.html

import bs4
import copy
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

    def __init__(self, env, line_n, text):
        self.book_n = env.book_n
        self.line_n = line_n
        self.text = text

    def __str__(self):
        return "{} {!r}".format(Locator(self.book_n, self.line_n), self.text)

class Environment:
    """Environment represents the context of a call to TEI.do_elem."""

    def __init__(self):
        self.book_n = None

    def copy(self):
        return copy.copy(self)

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
        # function. The current line number (line_n), and the partial contents
        # of the current line (partial) are shared in common across all calls,
        # in contrast to the Environment (env), which belongs to one call. The
        # flush function is called at the end of a line to yield a line to the
        # caller.
        line_n = None
        partial = []

        def flush(env):
            """Yield the lines represented by the current partial list and clear
            the list."""
            nonlocal line_n, partial

            text = "".join(partial).strip()
            partial.clear()
            if text:
                yield Line(env, line_n, text)

        def do_elem(root, env):
            nonlocal line_n, partial

            for elem in root.children:
                # Make a copy of the environment to pass to recursive calls to
                # do_elem. This allows them to know, for example, what book_n
                # they're in, while enabling us to remember the environment
                # before the call.
                sub_env = env.copy()

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
                        for x in flush(env):
                            yield x
                        cur_loc = Locator(env.book_n, line_n)
                        n = elem.get("n")
                        if n is not None:
                            # If the new line is marked with a number, check it
                            # against the previous line.
                            new_loc = Locator(env.book_n, n)
                            if not cur_loc.may_precede(new_loc):
                                warn("after line {!r}, expected {!r}, got {!r}".format(cur_loc, cur_loc.successor(), new_loc))
                        else:
                            # If no line number is provided, guess based on the
                            # previous line number.
                            new_loc = cur_loc.successor()
                        assert env.book_n == new_loc.book_n
                        line_n = new_loc.line_n
                    elif elem.name == "div1":
                        assert elem.get("type").lower() in ("book", "hymn"), elem.get("type")
                        sub_env.book_n = elem.get("n")
                        # Reset the line counter at the beginning of a new book.
                        line_n = None

                    if elem.name in ("milestone", "head", "gap", "pb", "note"):
                        pass
                    elif elem.name in ("div1", "div2", "l", "lb", "p", "q", "sp", "add", "del", "name"):
                        for x in do_elem(elem, sub_env):
                            yield x
                    else:
                        raise ValueError("don't understand element {!r}".format(elem.name))

                    if elem.name == "div1":
                        # At the end of a book, reset the line counter to be safe.
                        line_n = None
                else:
                    partial.append(betacode.decode(elem))
            for x in flush(env):
                yield x

        for x in do_elem(self.soup.find("text").body, Environment()):
            yield x
