# Lemmatization for Greek.
#
# Requires CLTK and the grc_models_cltk corpus. See:
#   https://docs.cltk.org/en/latest/installation.html
#   https://docs.cltk.org/en/latest/data.html
# python3 -c 'from cltk.data.fetch import FetchCorpus; FetchCorpus("grc").import_corpus("grc_models_cltk")'

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
    ("ἑκάεργος", "Ἑκάεργος"),
    ("ἑκάεργον", "Ἑκάεργος"),
    ("ἑκάεργε", "Ἑκάεργος"),
    ("ἑκαέργη", "Ἑκαέργη"),
    ("ἑκαέργην", "Ἑκαέργη"),
    ("α[ἶψα", "αἶψα"),
    ("παρήμενος", "πάρημαι"),
    ("παρήμενον", "πάρημαι"),
    ("παρήμενοι", "πάρημαι"),
    ("παρημένω", "πάρημαι"),
    ("δαιτί", "δαίς"),
    ("δαῖτας", "δαίς"),
    ("δαῖτες", "δαίς"),
    ("δαῖτας", "δαίς"),
    ("δαιτός", "δαίς"),
    ("Ζεῦ", "ζεύς"),
    ("ζεὺς", "ζεύς"),
    ("κραδίην", "καρδία"),
    ("ὀί̈ομαι", "οἴομαι"),
    ("ἠτίμασεν", "ἀτιμάω"),
    ("τρωσὶ", "τρώς"),
    ("τρωσὶν", "τρώς"),
    ("ἐννοσίγαι’", "ἐννοσίγαιος"),
    ("ἐννοσίγαιος", "ἐννοσίγαιος"),
    ("ἐί̈σης", "ἴσος"),
    ("τυδεί̈δῃ", "τυδεί̈δης"),
    ("προί̈ει", "προίημι"),
    ("αἰὼν", "αἰών"),
    ("ἐϊκυῖα", "εἰκός"),
    ("γεραιὲ", "γεραιός"),
    ("ἀχαιοὶ", "ἀχαιός"),
    ("ἀχιλλεὺς", "ἀχιλλεύς"),
    ("ἰδομενεὺς", "ἰδομενεύς"),
    ("ἤϋσεν", "αὔω"),
    ("χρειὼ", "χρειώ"),
    ("ἑοὺς", "ἑός"),
    ("πολεμήϊα", "πολεμήϊος"),
    ("φωνὴ", "φωνή"),
    ("βιὸν", "βιός"),
    ("πηλῆϊ", "πηλεύς"),
    ("τροχὸν", "τροχός"),
    ("ποιμὴν", "ποιμήν"),
    ("θαλερὸν", "θαλερός"),
    ("χροὶ̈", "χρώς"),
    ("ἀρχοὶ", "ἀρχός"),
    ("θαλερὴν", "θαλερός"),
    ("γνωτὸν", "γνωτός"),
    ("κρατερὰς", "κρατερός"),
    ("μηρὼ", "μηρός"),
    ("ἀργοὶ", "ἀργός"),
    ("κεῖσέ", "κεῖσε"),
    ("ἀχνύμενός", "ἀχεύω"),
    ("ζηνὸς", "ζεύς"),
    ("ἱδρὼς", "ἱδρώς"),
    ("τυδεί̈δην", "τυδεί̈δης"),
    ("χθιζὸν", "χθιζός"),
    ("δαὶ̈", "δάις"),
    ("κελαινὴ", "κελαινός"),
    ("ἀί̈ξας", "αίσσω"),
    ("ἔγχεί̈", "ἔγχος"),
    ("σφυρὸν", "σφυρός"),
    ("πυρκαϊῆς", "πυρκαϊά"),
    ("αἰχμὴν", "αἰχμή"),
    ("ὠκεανὸς", "ὠκεανός"),
    ("βαλὼν", "βάλλω"),
    ("ἰαχὴ", "ἰαχή"),
    ("διὶ", "ζεύς"),
    ("κεκληγὼς", "κλάζω"),
    ("ἡμέτερόν", "ἡμέτερος"),
    ("ἀχλὺς", "ἀχλύς"),
    ("παλλὰς", "παλλάς"),
    ("βοιωτοὶ", "βοιωτός"),
    ("λευκοὺς", "λευκός"),
    ("ἱερὸς", "ἱερός"),
    ("χαλεπὸς", "χαλεπός"),
    ("ζηνὶ", "ζεύς"),
    ("φυὴν", "φυή"),
    ("ζωοί", "ζωός"),
    ("χορὸν", "χορός"),
    ("ἐρεμνὴν", "ἐρεμνός"),
    ("χοροὶ", "χορός"),
    ("αἴσιμόν", "αἴσιμος"),
    ("φλογὶ", "φλόξ"),
    ("πολέμοιό", "πόλεμος"),
    ("δεῖμός", "δεῖμος"),
    ("ἐπεμβεβαὼς", "ἐπεμβαίνω"),
    ("οὔλυμπόν", "ὄλυμπος"),
    ("κὴρ", "κήρ"),
    ("αἰγὸς", "αἴξ"),
    ("περσεὺς", "περσεύς"),
    ("πρηνὴς", "πρηνής"),
    ("κεφαλαὶ", "κεφαλή"),
    ("βωμὸς", "βωμός"),
    ("εἴδεί̈", "εἶδος"),
    ("θνηταὶ", "θνητός"),
    ("οἶόν", "οἶος"),
    ("φυλόπιδός", "φύλοπις"),
    ("ἐὺς", "ἐύς"),
    ("ἀσπαστὸν", "ἀσπαστός"),
    ("ὁμὰ", "ὁμός"),
    ("ἡνίοχόν", "ἡνίοχος"),
    ("ἠνιόχην", "ἠνιόχης"),
    ("παλινάγρετός", "παλινάγρετος"),
    ("χαλεποὺς", "χαλεπός"),
    ("ῥύεταί", "ἐρύω"),
    ("ἄρηός", "ἄρης"),
    ("ἰφικλεί̈δην", "ἰφικλείδης"),
    ("ἀλκεί̈δαο", "ἀλκείδης"),
    ("κοί̈λην", "κοῖλος"),
    ("καββάλετ’", "καταβάλλω"),
    ("ὀιστοὶ", "ὀιστος"),
    ("ὑπολαμπὲς", "ὑπολαμπής"),
    ("προί̈ωξίς", "προίωξις"),
    ("παλίωξίς", "παλίωξις"),
    ("ὅμαδός", "ὅμαδος"),
    ("δαφοινεὸν", "δαφοινεός"),
    ("καναχῇσί", "καναχή"),
    ("ὁμιληδὸν", "ὁμιληδόν"),
    ("φρῖσσόν", "φρίσσω"),
    ("χλοῦναί", "χλούνης"),
    ("δρύαντά", "δρυάς"),
    ("ἐξάδιόν", "ἐξάδιος"),
    ("φάληρόν", "φάληρος"),
    ("πρόλοχόν", "πρόλοχος"),
    ("αἰγεί̈δην", "αἰγεί̈δης"),
    ("οἰωνιστὴν", "οἰωνιστής"),
    ("οὔρειόν", "οὔρειος"),
    ("πευκεί̈δας", "πευκείδης"),
    ("περιμήδεά", "περιμήδης"),
    ("δρύαλόν", "δρύαλος"),
    ("συναί̈γδην", "συναίγδης"),
    ("λιγὺ", "λιγύς"),
    ("κυκλοτερὴς", "κυκλοτερής"),
    ("ἐθοινῶντ’", "θοινάω"),
    ("ἁλιεὺς", "ἁλιεύς"),
    ("φαεινοὶ", "φαεινός"),
    ("ἄπλητοί", "ἄπλητος"),
    ("φαταὶ", "φατός"),
    ("δεινωπαὶ", "δεινωπός"),
    ("δαφοιναί", "δαφοινός"),
    ("ἄπληταί", "ἄπλητός"),
    ("κλωθὼ", "κλωθώ"),
    ("λάχεσίς", "λάχεσις"),
    ("ἀτροπος", "ἄτροπος"),
    ("χλωρὴ", "χλωρή"),
    ("ἀγλαί̈ῃς", "ἀγλαί̈α"),
    ("ἀγλαί̈ῃ", "ἀγλαί̈α"),
    ("ἀγλαί̈αι", "ἀγλαί̈α"),
    ("μελάνθησάν", "μελαίνω"),
    ("λαγὸς", "λαγών"),
    ("ῥυτὰ", "ῥυτός"),
    ("ἴδριές", "ἴδρις"),
    ("θεμιστονόην", "θεμιστονόη"),
    ("σαρκὸς", "σάρξ"),
    ("λωβητὸς", "λωβητός"),
    ("ἀποθρῴσκωσιν", "ἀποθρῴσκω"),
    ("ἀλλήλῃς", "ἀλλήλλων"),
    ("αἴγειροί", "αἴγειρος"),
    ("ἰαωλκὸς", "ἰαωλκός"),
    ("ἄνθειά", "ἄνθεια"),
    ("προϊδέσθαι", "προεῖδον"),
    ("ὀρθὰς", "ὀρθός"),
    ("ἄραβός", "ἄραβος"),
    ("κόρυθός", "κόρυθος"),
    ("ἐπιθρῴσκουσα", "ἐπιθρῴσκω"),
    ("εἴκελά", "εἴκελος"),
    ("κακτάμεναι", "κατακτάομαι"),
    ("νίσσοντ’", "νίσσομαι"),
    ("ἀιδὲς", "ἀιδής"),
    ("κυδοιμὸς", "κυδοιμός"),
    ("κυδοιμὸν", "κυδοιμός"),
    ("ὑμεναίου", "ὑμέναιος"),
    ("ὑμεναίους", "ὑμέναιος"),
    ("ὑμεναίων", "ὑμέναιος"),
    ("χάρμης", "χάρμη"),
    ("λαιμῷ", "λαιμός"),
    ("λαιμοῖο", "λαιμός"),
    ("κεραυνῶν", "κεραυνός"),
    ("κεραυνοί", "κεραυνός"),
    ("πηληι+άδης", "πηλείδης"),
    ("πηληϊάδαο", "πηλείδης"),
    ("προΐαψεν", "προϊάπτω"),
    ("ἀπερείσι’", "ἀπερείσιος"),
    ("Ὀλύμπια", "Ὀλύμπιος"),
    ("οἶκόνδε", "οἶκος"),
    ("οἶκόνδ’", "οἶκος"),
    ("οὔτ’", "οὔτε"),
    ("οὔθ’", "οὔτε"),
)

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
lemmatizer = DictLemmatizer(dict(
    (map(cltk_normalize, x) for x in OVERRIDES)
), source = "Sedes overrides", backoff = cltk_lemmatizer.lemmatizer, verbose = cltk_lemmatizer.VERBOSE)

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
