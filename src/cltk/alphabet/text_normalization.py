"""Functions for preprocessing texts. Not language-specific."""

from unicodedata import normalize


def cltk_normalize(text, compatibility=True):
    if compatibility:
        return normalize("NFKC", text)
    else:
        return normalize("NFC", text)
