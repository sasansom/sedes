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

COUNTS = {}
LINES = []

with open("theogony.beta") as f:
    lineno = 0
    for line in f:
        line = line.strip()
        if line == "":
            continue
        lineno += 1
        LINES.append(line)
        key = "".join([tone_of(syl) for syl in syllables(line)])
        COUNTS.setdefault(key, [])
        COUNTS[key].append(lineno)

for key, lines in sorted(COUNTS.items(), key=lambda x: len(x[1])):
    print "%-20s %s" % (key, ", ".join("%4d"%x for x in lines))
    for line in lines:
        print LINES[line-1]
    print
