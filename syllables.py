#!/usr/bin/env python
# coding: utf-8

import codecs
import re
import sys
import unicodedata

import beta

VOWELS = ur'[αΑεΕηΗιΙοΟωΩυΥ]'
CONSONANTS = ur'[βΒξΞδΔφΦγΓκΚλΛμΜνΝπΠθΘρΡςΣσϲϹτΤϝϜχΧψΨζΖ]'
DIACRITICALS = ur'[\u0313\u0314\u0301\u0342\u0300\u0308\u0345\u0323]'

def syllables(s):
    return re.findall(ur'(?:%(c)s(?:’ +)?)?(?:%(v)s%(v)s%(d)s*|%(v)s%(d)s*)(?:%(c)s’?)?' % {"c": CONSONANTS, "v": VOWELS, "d": DIACRITICALS}, s, flags=re.UNICODE)

def tone_of(syl):
    if u"\u0301" in syl:
        return "/"
    if u"\u0300" in syl:
        return "\\"
    if u"\u0342" in syl:
        return "="
    return "."

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
<table>
"""

IMG_MAP = {
    ".": "1.png",
    "/": "2.png",
    "\\": "3.png",
    "=": "4.png",
}

with codecs.open("theogony.beta", encoding="utf-8") as f:
    for beta_line in f:
        beta_line = beta_line.strip()
        line = beta.decode(beta_line)
        if line == u"":
            print "<tr></tr>"
            continue
        print "<tr>"
        print "<td>"
        for syl in syllables(line):
            sys.stdout.write("<img src=%s>" % IMG_MAP[tone_of(syl)])
        print "</td>"
        print "<td>" + unicodedata.normalize("NFC", line).encode("utf-8") + "</td>"
        print "<td>" + u"–".join(syllables(line)).encode("utf-8") + "</td>"
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
