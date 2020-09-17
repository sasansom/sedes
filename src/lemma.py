# Lemmatization for Greek.

import unicodedata

# https://docs.cltk.org/en/latest/greek.html#lemmatization-backoff-method
from cltk.lemmatize.greek.backoff import BackoffGreekLemmatizer
# https://docs.cltk.org/en/latest/greek.html#normalization
from cltk.corpus.utils.formatter import cltk_normalize

__all__ = ["lookup"]

lemmatizer = BackoffGreekLemmatizer()

def lookup(word, default=None):
    # The CLTK lemmatizer expects its input to be normalized according to
    # cltk_normalize, but our convention elsewhere is to always use NFD
    # normalization.
    return unicodedata.normalize("NFD", lemmatizer.lemmatize([cltk_normalize(word)])[0][1])
