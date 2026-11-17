"""Module for lemmatizing Ancient Greek."""

__author__ = ["Patrick J. Burns <patrick@diyclassics.org>"]
__license__ = "MIT License. See LICENSE."

import os

from cltk.lemmatize.backoff import (
    DictLemmatizer,
    IdentityLemmatizer,
    RegexpLemmatizer,
    UnigramLemmatizer,
)
CLTK_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "cltk_data")
import pickle
def open_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)

greek_sub_patterns = [("(ων)(ος|ι|να)$", r"ων")]

models_path = os.path.normpath(
    os.path.join(CLTK_DATA_DIR, "grc", "model", "grc_models_cltk", "lemmata", "backoff")
)


class GreekBackoffLemmatizer:
    """Suggested backoff chain; includes at least on of each
    type of major sequential backoff class from backoff.py.
    """

    def __init__(self, train: list[list] = None, seed: int = 3, verbose: bool = False):
        missing_models_message = "GreekBackoffLemmatizer requires the ```grc_models_cltk``` to be in cltk_data. Please load this corpus."

        try:
            greek_lemmatized_sents = open_pickle(
                os.path.join(models_path, "greek_lemmatized_sents.pickle")
            )
            GREEK_OLD_MODEL = open_pickle(
                os.path.join(models_path, "greek_lemmata_cltk.pickle")
            )
            GREEK_MODEL = open_pickle(
                os.path.join(models_path, "greek_model.pickle")
            )
        except FileNotFoundError as err:
            raise type(err)(missing_models_message)

        self.VERBOSE = verbose

        def _randomize_data(train: list[list], seed: int):
            import random

            random.seed(seed)
            random.shuffle(train)
            train_size = int(0.9 * len(train))
            pos_train_sents = train[:train_size]
            lem_train_sents = [[(item[0], item[1]) for item in sent] for sent in train]
            train_sents = lem_train_sents[:train_size]
            test_sents = lem_train_sents[train_size:]

            return pos_train_sents, train_sents, test_sents

        _pos_train_sents, train_sents, test_sents = _randomize_data(
            greek_lemmatized_sents, seed
        )
        self.test_sents = test_sents # Used in evaluate.

        # Suggested backoff chain--should be tested for optimal order
        backoff1 = IdentityLemmatizer(verbose=verbose)
        backoff2 = DictLemmatizer(
            lemmas=GREEK_OLD_MODEL,
            source="Morpheus Lemmas",
            backoff=backoff1,
            verbose=verbose,
        )
        backoff3 = RegexpLemmatizer(
            greek_sub_patterns,
            source="CLTK Greek Regex Patterns",
            backoff=backoff2,
            verbose=verbose,
        )
        backoff4 = UnigramLemmatizer(
            train_sents,
            source="CLTK Sentence Training Data",
            backoff=backoff3,
            verbose=verbose,
        )
        backoff5 = DictLemmatizer(
            lemmas=GREEK_MODEL,
            source="Greek Model",
            backoff=backoff4,
            verbose=verbose,
        )
        self.lemmatizer = backoff5

    def lemmatize(self, tokens: list[str]):
        """
        Lemmatize a list of words.

        >>> lemmatizer = GreekBackoffLemmatizer()
        >>> from cltk.alphabet.text_normalization import cltk_normalize
        >>> word = cltk_normalize('διοτρεφές')
        >>> lemmatizer.lemmatize([word])
        [('διοτρεφές', 'διοτρεφής')]
        >>> republic = cltk_normalize("κατέβην χθὲς εἰς Πειραιᾶ μετὰ Γλαύκωνος τοῦ Ἀρίστωνος")
        >>> lemmatizer.lemmatize(republic.split())
        [('κατέβην', 'καταβαίνω'), ('χθὲς', 'χθές'), ('εἰς', 'εἰς'), ('Πειραιᾶ', 'Πειραιεύς'), ('μετὰ', 'μετά'), ('Γλαύκωνος', 'Γλαύκων'), ('τοῦ', 'ὁ'), ('Ἀρίστωνος', 'Ἀρίστων')]
        """

        lemmas = self.lemmatizer.lemmatize(tokens)
        return lemmas

    def evaluate(self):
        if self.VERBOSE:
            raise AssertionError(
                "evaluate() method only works when verbose: bool = False"
            )
        return self.lemmatizer.evaluate(self.test_sents)

    def __repr__(self):
        return f"<BackoffGreekLemmatizer v0.1>"

    def __call__(self, token: str) -> str:
        return self.lemmatize([token])[0][0]
