#!/usr/bin/env python

import re

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

print SENTENCE
print syllables(SENTENCE)
print " ".join([tone_of(syl) for syl in syllables(SENTENCE)])

with open("theogony.beta") as f:
    for line in f:
        print " ".join([tone_of(syl) for syl in syllables(line)])
