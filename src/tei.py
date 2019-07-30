# https://tei-c.org/release/doc/tei-p5-doc/en/html/index.html

import bs4
import re
import sys

import betacode

def warn(msg):
    print("warning: {}".format(msg), file=sys.stderr)

class NullLocator:
    def successor(self):
        return Locator(1, "")

    def may_succeed(self, other):
        return False

    def __str__(self):
        return "0"

class Locator:
    def __init__(self, number, letter):
        self.number = number
        self.letter = letter

    @staticmethod
    def parse(s):
        m = re.match(r'^(\d+)(\w*)$', s, flags=re.ASCII)
        if not m:
            raise ValueError("cannot parse line number {!r}".format(s))
        number, letter = m.groups()
        try:
            number = int(number)
        except ValueError:
            raise ValueError("cannot parse line number {!r}".format(s))
        return Locator(number, letter)

    def successor(self):
        return Locator(self.number + 1, "")

    def may_precede(self, other):
        return (other.number == self.number + 1 and (other.letter == "" or other.letter == "a")) \
            or (other.number == self.number and self.letter == "" and other.letter == "a") \
            or (other.number == self.number and self.letter != "" and other.letter == chr(ord(self.letter) + 1))

    def __str__(self):
        return "{}{}".format(self.number, self.letter)

class Line:
    def __init__(self, n, text):
        self.n = n
        self.text = text

    def __str__(self):
        return "{} {!r}".format(self.n, self.text)

class TEI:
    def __init__(self, f):
        self.soup = bs4.BeautifulSoup(f, "xml")

    @property
    def title(self):
        return self.soup.teiHeader.fileDesc.titleStmt.title.get_text()

    @property
    def author(self):
        return self.soup.teiHeader.fileDesc.titleStmt.author.get_text()

    def lines(self):
        line_n = NullLocator()
        partial = []

        def flush():
            nonlocal line_n, partial
            text = "".join(partial).strip()
            partial = []
            if text:
                yield Line(line_n, text)

        def do_elem(root):
            nonlocal line_n, partial
            for elem in root.children:
                if type(elem) == bs4.element.Comment:
                    pass
                elif type(elem) == bs4.element.Tag:
                    if elem.name in ("l", "lb"):
                        # Output previous line.
                        for x in flush():
                            yield x
                        n = elem.get("n")
                        if n is not None:
                            # If new new line is marked with a number, check it
                            # against the previous line.
                            new_n = Locator.parse(n)
                            if not line_n.may_precede(new_n):
                                warn("after line {}, expected {}, got {!r}".format(line_n, line_n.successor(), n))
                            line_n = new_n
                        else:
                            # If no line number is provided, guess based on the
                            # previous line number.
                            line_n = line_n.successor()

                    if elem.name in ("milestone", "head", "gap"):
                        pass
                    elif elem.name in ("div1", "div2", "l", "lb", "p", "q", "sp", "add", "del"):
                        for x in do_elem(elem):
                            yield x
                    else:
                        raise ValueError("don't understand element {!r}".format(elem.name))
                else:
                    partial.append(betacode.decode(elem))
            for x in flush():
                yield x

        for x in do_elem(self.soup.find("text").body):
            yield x
