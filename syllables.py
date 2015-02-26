#!/usr/bin/env python

import re
import sys

CONSONANTS = "bcdfgklmnpqrstvxyz"
VOWELS = "aehiouw"

def syllables(s):
    return re.findall('[*()/\\=+|' + CONSONANTS + ']?[*()/\\=+|' + VOWELS + ']{1,2}[*()/\\=+|' + CONSONANTS + ']*\'?', s)

def tone_of(syl):
    if "/" in syl:
        return "/"
    if "\\" in syl:
        return "\\"
    if "=" in syl:
        return "="
    return "."

# mous a/ wn *(el ik wn i a/d wn a)rx w/m eq' a) ei/d ein
# SENTENCE = "mousa/wn *(elikwnia/dwn a)rxw/meq' a)ei/dein,"
# SENTENCE = "h)\ *(/ippou krh/nhs h)\ *)olmeiou= zaqe/oio"
# print SENTENCE
# print " ".join(syllables(SENTENCE))

# sys.exit()

print """\
<!DOCTYPE html>
<html>
<head>
<meta charset=utf-8>
<style>
p {
    line-spacing: 0.5em;
}
</style>
</head>
<body>
<p>
"""

IMG_MAP = {
    ".": "1.png",
    "/": "2.png",
    "\\": "3.png",
    "=": "4.png",
}

with open("theogony.beta") as f:
    for line in f:
        line = line.strip()
        if line == "":
            print "</p><p>"
            continue
        for syl in syllables(line):
            sys.stdout.write("<img src=%s>" % IMG_MAP[tone_of(syl)])
        print "<br>"

print """
</p>
</body>
</html>
"""
