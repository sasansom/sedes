# coding: utf-8

LOWER = list(u"αβγδεζηθικλμνξοπρστυφχψω")
LOWER_SOUNDS = list(u"αβγδεζηθι") + [u"κχ"] + list(u"λμνξο") + [u"πφ"] + list(u"ρστυψω")

# Canonicalize a bare Greek letter.
def canon(c):
    c = c.lower()
    if c == u"ς":
        c = u"σ"
    return c

# Canonicalize and additionally combine π/φ and κ/χ.
def canon_sounds(c):
    c = canon(c)
    if c in (u"π", u"φ"):
        c = u"πφ"
    elif c in (u"κ", u"χ"):
        c  = u"κχ"
    return c
