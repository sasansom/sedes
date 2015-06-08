#!/usr/bin/env python
# coding: utf-8

import codecs
import re
import sys
import unicodedata

import betacode

VOWELS = ur'[αΑεΕηΗιΙοΟωΩυΥ]'
CONSONANTS = ur'[βΒξΞδΔφΦγΓκΚλΛμΜνΝπΠθΘρΡςΣσϲϹτΤϝϜχΧψΨζΖ]'
DIACRITICALS = ur'[\u0313\u0314\u0301\u0342\u0300\u0308\u0345\u0323]'

def syllabify(s):
    return re.findall(ur'(?:%(c)s(?:’ +)?)?(?:%(v)s%(v)s%(d)s*|%(v)s%(d)s*)(?:%(c)s’?)?' % {"c": CONSONANTS, "v": VOWELS, "d": DIACRITICALS}, s, flags=re.UNICODE)

def tone_of(syl):
    if u"\u0301" in syl:
        return "/"
    if u"\u0342" in syl:
        return "="
    # Grave accent or no diacritical.
    return "."

def nfc(u):
    return unicodedata.normalize("NFC", u)

print """\
<!DOCTYPE html>
<html>
<head>
<meta charset=utf-8>
</head>
<body>
<table>
<tr>
<th>line</th>
<th>tone pattern</th>
<th>line</th>
<!-- <th>syllabification</th> -->
<th>same tones</th>
</tr>
"""

IMG_MAP = {
    ".": "1.png",
    "/": "2.png",
    "\\": "3.png",
    "=": "4.png",
}

LINES = []
TONE_PATTERN_MAP = {}

with codecs.open("theogony.beta", encoding="utf-8") as f:
    lineno = 0
    for beta_line in f:
        beta_line = beta_line.strip()
        line = betacode.decode(beta_line)
        LINES.append(line)
        if line == u"":
            continue
        lineno += 1
        syllables = syllabify(line)
        tone_pattern = "".join(tone_of(syl) for syl in syllables)
        TONE_PATTERN_MAP.setdefault(tone_pattern, [])
        TONE_PATTERN_MAP[tone_pattern].append(lineno)

lineno = 0
for line in LINES:
    if line == u"":
        print "<tr><td>&nbsp;</td></tr>"
        continue
    lineno += 1
    print "<tr id=l%d>" % lineno
    print "<td align=right><a href=\"#l%d\">%d</a></td>" % (lineno, lineno)
    imgs = []
    syllables = syllabify(line)
    for syl in syllables:
        imgs.append("<img src=%s>" % IMG_MAP[tone_of(syl)])
    print "<td>" + "".join(imgs) + "</td>"
    print "<td>" + nfc(line.replace(u" ", u"&nbsp;")).encode("utf-8") + "</td>"
    # print "<td>" + nfc(u"–".join(syllables)).encode("utf-8") + "</td>"
    tone_pattern = "".join(tone_of(syl) for syl in syllables)
    links = []
    for other_lineno in TONE_PATTERN_MAP[tone_pattern]:
        if other_lineno == lineno:
            links.append("%d" % other_lineno)
        else:
            links.append("<a href=\"#l%d\">%d</a>" % (other_lineno, other_lineno))
    print "<td>" + "&nbsp;".join(links) + "</td>"
    print "</tr>"

print """
</table>
</body>
</html>
"""

# with open("theogony.beta") as f:
#     lineno = 0
#     for line in f:
#         line = line.strip()
#         if line == "":
#             continue
#         lineno += 1
#         LINES.append(line)
#         for syl in syllables(line):
#             tone = tone_of(syl)
#             COUNTS.setdefault(tone, 0)
#             COUNTS[tone] += 1
# 
# for key, count in sorted(COUNTS.items(), key=lambda x: x[1]):
#     print "%s %s" % (key, count)
