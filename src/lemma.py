# Lemmatization for Greek.
#
# Requires CLTK and the grc_models_cltk corpus. See:
#   https://docs.cltk.org/en/latest/installation.html
#   https://docs.cltk.org/en/latest/data.html
# python3 -c 'from cltk.data.fetch import FetchCorpus; FetchCorpus("grc").import_corpus("grc_models_cltk")'

import csv
import os
import os.path
import re
import unicodedata

try:
    from cltk.lemmatize.grc import GreekBackoffLemmatizer
    from cltk.lemmatize.backoff import DictLemmatizer
    from cltk.alphabet.text_normalization import cltk_normalize
except ModuleNotFoundError as e:
    e.msg += ". Run:\nsource venv/bin/activate"
    raise

__all__ = ["lookup"]

OVERRIDES = {}
with open(os.path.join(os.path.dirname(__file__), "lemma-overrides.csv")) as f:
    for row in csv.DictReader(f):
        word = cltk_normalize(row["word"])
        lemma = cltk_normalize(row["lemma"])
        assert word not in OVERRIDES, word
        OVERRIDES[word] = lemma

# Looks for the rightmost sequence of one or more vowels and diacritics,
# followed by zero or more non-vowels.
FINAL_VOWEL_CLUSTER_RE = re.compile("([αεηιουω\u0313\u0314\u0301\u0342\u0300\u0308\u0345\u0323]+)[^αεηιουω]*$", re.I)

# We help the lemmatizer out by trying a few transformed variations on the
# original word, in case there is no lemma found for the original word. The
# transformations involve diacritics in the final syllable:
#   change a grave accent to an acute accent
#   remove an acute accent
# We try the original word, followed by each transformation in order, stopping
# that the first one for which lemmatization succeeds.
# https://github.com/sasansom/sedes/issues/29
#
# Instead of looking for the final "syllable," we look for the final subsequence
# of vowels and diacritics, which is almost the same. This could result in false
# transformations for words in which the final vowel cluster represents more
# than one syllable, and which have a transformable diacritic on a non-final
# syllable, like "ἁθρόοι" or "Ἠελίοιο". This should not be a problem for the
# purpose of augmented lemmatization, however.
def pre_transformations(word):
    yield word

    vowels = FINAL_VOWEL_CLUSTER_RE.search(word)
    if vowels is None:
        return

    seen = set([word])
    for old, new in (
        ("\u0300", "\u0301"), # grave → acute
        ("\u0301", ""),       # acute → no accent
    ):
        start, end = vowels.span()
        transformed = word[:start] + vowels.group().replace(old, new) + word[end:]
        if transformed not in seen:
            yield transformed
            seen.add(transformed)

# Set verbose = True in order to find out what lemmatizer in the backoff chain
# is responsible for the returned result. We want to ignore lemmata that come
# from IdentityLemmatizer in the lookup loop below, because a returned identity
# lemma would otherwise prevent us from trying the next pre-transformation.
cltk_lemmatizer = GreekBackoffLemmatizer(verbose = True)
# Insert our own lookup of hardcoded lemmata before the CTLK process.
lemmatizer = DictLemmatizer(OVERRIDES,
    source = "Sedes overrides", backoff = cltk_lemmatizer.lemmatizer, verbose = cltk_lemmatizer.VERBOSE)

# Returns None if no lemma was found.
def lookup(word):
    for transformed in pre_transformations(word):
        # The CLTK lemmatizer expects its input to be normalized according to
        # cltk_normalize, but our convention elsewhere is to always use NFD
        # normalization.
        _, lemma, source = lemmatizer.lemmatize([cltk_normalize(transformed)])[0]
        # IdentityLemmatizer is the last link in the backoff chain. If that's
        # the source of the lemma, ignore it, in order to try again with the
        # next pre-transformation.
        if lemma and source != "<IdentityLemmatizer>":
            return unicodedata.normalize("NFD", lemma)

# Run this module as a command to find lemmata from the command line.
# python3 lemma.py βιὸν
if __name__ == "__main__":
    import sys
    error = False
    for arg in sys.argv[1:]:
        word = unicodedata.normalize("NFD", arg)
        lemma = lookup(word)
        print(f"{word}\t{lemma}")
