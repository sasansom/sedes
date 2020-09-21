# Lemmatization for Greek.
#
# Requires CLTK and the greek_models_cltk corpus. See:
#   https://docs.cltk.org/en/latest/installation.html
#   https://docs.cltk.org/en/latest/importing_corpora.html
# python3 -c 'from cltk.corpus.utils.importer import CorpusImporter; CorpusImporter("greek").import_corpus("greek_models_cltk")'

import unicodedata

# https://docs.cltk.org/en/latest/greek.html#lemmatization-backoff-method
from cltk.lemmatize.greek.backoff import BackoffGreekLemmatizer
from cltk.lemmatize.backoff import DictLemmatizer
# https://docs.cltk.org/en/latest/greek.html#normalization
from cltk.corpus.utils.formatter import cltk_normalize

__all__ = ["lookup"]

OVERRIDES = (
    ("τ’", "τε"),
    ("σ’", "σύ"),
    ("ἀοιδοὶ", "ἀοιδός"),
    ("ἀοιδαὶ", "ἀοιδή"),
    ("ἀοιδὰν", "ἀοιδή"),
    ("ἀοιδοῖς", "ἀοιδός"),
    ("ἀοιδοῦ", "ἀοιδός"),
    ("ἀοιδὴ", "ἀοιδή"),
    ("ἀοιδή’", "ἀοιδή"),
    ("ἀοιδοὺς", "ἀοιδός"),
    ("πηληϊάδεω", "πηλείδης"),
    ("ἄλγε’", "ἄλγος"),
    ("ἄϊδι", "ἅιδης"),
    ("προί̈αψεν", "προιάπτω"),
    ("διὸς", "ζεύς"),
    ("οἰωνοῖσί", "οἰωνός"),
    ("ὀδυσῆί̈", "ὀδυσσεύς"),
    ("ὀδυσῆϊ", "ὀδυσσεύς"),
    ("ὀδυσεὺς", "ὀδυσσεύς"),
    ("ὀδυσσεὺς", "ὀδυσσεύς"),
    ("ἑκάεργος", "ἑκάεργος"),
    ("α[ἶψα", "αἶψα"),
    ("παρήμενος", "πάρημαι"),
    ("παρήμενον", "πάρημαι"),
    ("παρήμενοι", "πάρημαι"),
    ("παρημένω", "πάρημαι"),
)

cltk_lemmatizer = BackoffGreekLemmatizer()
# Insert our own lookup of hardcoded lemmata before the CTLK process.
lemmatizer = DictLemmatizer(dict(
    (map(cltk_normalize, x) for x in OVERRIDES)
), source = "Sedes overrides", backoff = cltk_lemmatizer.lemmatizer, verbose = cltk_lemmatizer.VERBOSE)

def lookup(word, default=None):
    # The CLTK lemmatizer expects its input to be normalized according to
    # cltk_normalize, but our convention elsewhere is to always use NFD
    # normalization.
    return unicodedata.normalize("NFD", lemmatizer.lemmatize([cltk_normalize(word)])[0][1])
