#!/usr/bin/env python

import re
import sys

CONSONANTS = "bcdfgklmnpqrstvxyz"
VOWELS = "aehiouw"

def syllables(s):
    return re.findall(r'[*()/\\=+|' + CONSONANTS + r']?[*()/\\=+|' + VOWELS + r']{1,2}[*()/\\=+|' + CONSONANTS + ']*\'?', s)

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
        for syl in syllables(line):
            tone = tone_of(syl)
            COUNTS.setdefault(tone, 0)
            COUNTS[tone] += 1

for key, count in sorted(COUNTS.items(), key=lambda x: x[1]):
    print "%s %s" % (key, count)
