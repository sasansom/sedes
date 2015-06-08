#!/usr/bin/env python
# coding: utf-8

import codecs
import getopt
import math
import sys
import unicodedata

import betacode

COLOR_B = (240, 163, 255)
COLOR_A = (25, 25, 25)

def entropy(a):
    sum = 0.0
    for x in set(a):
        p = float(a.count(x)) / len(a)
        sum += -p * math.log(p, 2)
    return sum

def nfc(u):
    return unicodedata.normalize("NFC", u)

def mean(a):
    return float(sum(a)) / len(a)

def blend_linear(colors):
    r = mean([rgb[0] for rgb in colors])
    g = mean([rgb[1] for rgb in colors])
    b = mean([rgb[2] for rgb in colors])
    return r, g, b

def srgb_to_linear_component(c):
    f = c / 255.0
    if f <= 0.04045:
        return (f / 12.92) * 255
    else:
        return (((f+0.055) / 1.055)**2.4) * 255

def srgb_to_linear(srgb):
    return tuple(map(srgb_to_linear_component, srgb))

def linear_to_srgb_component(c):
    f = c / 255.0
    if f <= 0.0031308:
        return (12.92 * f) * 255
    else:
        return (f**(1/2.4) * 1.055 - 0.055) * 255

def linear_to_srgb(linear):
    return tuple(map(linear_to_srgb_component, linear))

def blend_srgb(colors_srgb):
    """Blend RGB triples assumed to be in the sRGB colorspace."""
    # We first convert sRGB values into a linear space, do a linear blend, and
    # then convert back into sRGB space.
    # http://www.4p8.com/eric.brasseur/gamma.html#formulas
    # https://en.wikipedia.org/wiki/SRGB#Specification_of_the_transformation
    colors_lrgb = map(srgb_to_linear, colors_srgb)
    linear = blend_linear(colors_lrgb)
    return linear_to_srgb(linear)

def interp_srgb(ca, cb, p):
    sca = srgb_to_linear(ca)
    scb = srgb_to_linear(cb)
    linear = (
        sca[0] + p * (scb[0] - sca[0]),
        sca[1] + p * (scb[1] - sca[1]),
        sca[2] + p * (scb[2] - sca[2]),
    )
    return linear_to_srgb(linear)

def round_color(rgb):
    return tuple(int(c + 0.5) for c in rgb)

# Is this a word we want to consider?
WORD_BLACKLIST = set([u"τε", u"τ’"])
def admit_word(word):
    return word.lower() not in WORD_BLACKLIST

CANONICAL_LETTERS = {
    u"κ": u"κ/χ",
    u"Κ": u"Κ/Χ",
    u"χ": u"κ/χ",
    u"Χ": u"Κ/Χ",
    u"φ": u"φ/π",
    u"Φ": u"Φ/Π",
    u"π": u"φ/π",
    u"Π": u"Φ/Π",
}
def canonicalize_letter(l):
    return CANONICAL_LETTERS.get(l, l).lower()

opts, args = getopt.gnu_getopt(sys.argv[1:], "")

input_filename, = args

LINES = []
with codecs.open(input_filename, encoding="utf-8") as f:
    for line in f:
        LINES.append(line.strip())

print """\
<!DOCTYPE html>
<html>
<head>
<meta charset=utf-8>
<style>
table {
    cell-spacing: 0;
    cell-padding: 0;
}
</style>
</head>
<body>
"""

ENTROPY = []
min_entropy = 1.0
max_entropy = 0.0

LOWEST_ENTROPY_LINES = []

for lineno in range(len(LINES)):
    words = []
    if lineno - 1 >= 0:
        words.extend(LINES[lineno-1].split())
    words.extend(LINES[lineno].split())
    if lineno + 1 < len(LINES):
        words.extend(LINES[lineno+1].split())
    letters = []
    for word in words:
        if admit_word(word):
            letters.append(canonicalize_letter(word[0]))
    entropy_per_word = entropy(letters) / len(words)
    if entropy_per_word < min_entropy:
        min_entropy = entropy_per_word
    if entropy_per_word > max_entropy:
        max_entropy = entropy_per_word
    ENTROPY.append(entropy_per_word)

    if len(LOWEST_ENTROPY_LINES) < 10 or entropy_per_word < ENTROPY[LOWEST_ENTROPY_LINES[9]]:
        LOWEST_ENTROPY_LINES.append(lineno)
        LOWEST_ENTROPY_LINES.sort(key=lambda x: ENTROPY[x])
        LOWEST_ENTROPY_LINES = LOWEST_ENTROPY_LINES[:10]

print """\
<h2>Index of lines with least entropy</h2>
<table>
<thead>
<tr>
<th>#</th>
<th>entropy per word</th>
<th>line</th>
</tr>
</thead>
<tbody>
"""

for lineno in LOWEST_ENTROPY_LINES:
    line = LINES[lineno]
    entropy_per_word = ENTROPY[lineno]
    print "<tr>"
    print "<td align=right><a href=\"#l%d\">%d</a></td>" % (lineno+1, lineno+1)
    print "<td align=center>%.3f</td>" % entropy_per_word
    print "<td style='background-color: rgb(%d,%d,%d);'>" % round_color(interp_srgb(COLOR_A, COLOR_B, (entropy_per_word - min_entropy) / (max_entropy - min_entropy)))
    print nfc(line.replace(u" ", u"&nbsp;")).encode("utf-8") + "</td>"
    print "</tr>"

print """\
</tbody>
</table>
<h2>Poem</h2>
<table>
<tr>
<th>#</th>
<th>entropy per word</th>
<th>line</th>
</tr>
"""

for lineno in range(len(LINES)):
    line = LINES[lineno]
    entropy_per_word = ENTROPY[lineno]
    print "<tr id=l%d>" % (lineno+1)
    print "<td align=right><a href=\"#l%d\">%d</a></td>" % (lineno+1, lineno+1)
    print "<td align=center>%.3f</td>" % entropy_per_word
    print "<td style='background-color: rgb(%d,%d,%d);'>" % round_color(interp_srgb(COLOR_A, COLOR_B, (entropy_per_word - min_entropy) / (max_entropy - min_entropy)))
    print nfc(line.replace(u" ", u"&nbsp;")).encode("utf-8") + "</td>"
    print "</tr>"

print """
</table>
</body>
</html>
"""
