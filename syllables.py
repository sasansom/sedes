#!/usr/bin/env python

import re
import sys

CONSONANTS = "bcdfgklmnpqrstvxyz"
VOWELS = "aehiouw"

def syllables(s):
    return re.findall(r'[*()/\\=+|' + CONSONANTS + r']?[*()/\\=+|' + VOWELS + r']+[*()/\\=+|' + CONSONANTS + ']*\'?', s)

def tone_of(syl):
    if "/" in syl:
        return "/"
    if "\\" in syl:
        return "\\"
    if "=" in syl:
        return "="
    return "."

SENTENCE = "mousa/wn *(elikwnia/dwn a)rxw/meq' a)ei/dein,"

print """\
<!DOCTYPE html>
<html>
<head>
<meta charset=utf-8>
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
