#!/usr/bin/env python

import codecs
import math
import sys
import unicodedata

import beta

COLOR_B = (240, 163, 255)
COLOR_A = (25, 25, 25)

def entropy(a):
    sum = 0.0
    for x in set(a):
        p = float(a.count(x)) / len(a)
        sum += -p * math.log(p, 2)
    return sum

LINES = []

lineno = 0
with codecs.open("theogony.beta", encoding="utf-8") as f:
    for beta_line in f:
        beta_line = beta_line.strip()
        line = beta.decode(beta_line)
        if not line:
            continue
        LINES.append(line)

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
    #
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
<table>
<tr>
<th>line</th>
<th>entropy per word</th>
<th>line</th>
</tr>
"""

ENTROPY = []
min_entropy = 1.0
max_entropy = 0.0

for lineno in range(len(LINES)):
    words = []
    if lineno - 1 >= 0:
        words.extend(LINES[lineno-1].split())
    words.extend(LINES[lineno].split())
    if lineno + 1 < len(LINES):
        words.extend(LINES[lineno+1].split())
    letters = [word[0] for word in words]
    entropy_per_word = entropy(letters) / len(words)
    if entropy_per_word < min_entropy:
        min_entropy = entropy_per_word
    if entropy_per_word > max_entropy:
        max_entropy = entropy_per_word
    ENTROPY.append(entropy_per_word)

for lineno in range(len(LINES)):
    line = LINES[lineno]
    entropy_per_word = ENTROPY[lineno]
    print "<tr id=l%d>" % lineno
    print "<td align=right><a href=\"#l%d\">%d</a></td>" % (lineno, lineno)
    print "<td align=center>%.3f</td>" % entropy_per_word
    print "<td style='background-color: rgb(%d,%d,%d);'>" % round_color(interp_srgb(COLOR_A, COLOR_B, (entropy_per_word - min_entropy) / (max_entropy - min_entropy)))
    print nfc(line.replace(u" ", u"&nbsp;")).encode("utf-8") + "</td>"
    print "</tr>"

print """
</table>
</body>
</html>
"""
