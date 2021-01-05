# -*- coding: utf-8 -*-
from typing import List, Dict

from unidecode import unidecode
from sklearn.feature_extraction.text import TfidfVectorizer
# spaCy is a free, open-source library for advanced Natural Language Processing (NLP) in Python.
import spacy
from functools import partial

from collections import Counter
import re

import logging
logger = logging.Logger(name='Utils Logger')


def load_models(corpus: List[str], language: str):
    """
    Build TF-IDF vectorize and features from a given corpus.

    :param corpus: List of strings from which we want to extract features.
    :param language: Language of the corpus.
    :return:
    TODO complete
    """

    # We replace the default tokenizer from sklearn by one using spaCy # TODO: why are we doing that?
    def tokenize(nlp, text):
        # Cut the text into individual tokens removing stop words, punctuations, numbers, symbols and spaces
        return [unidecode(w.text.lower()) for w in nlp(text)
                if w.pos_ not in ["PUNCT", "NUM", "SYM", "SPACE"] and w.is_stop is False]
    # Load spacy language model
    nlp = spacy.load(language)
    # Allows to send the nlp argument in the callback function passed to TfidfVectorizer
    t = partial(tokenize, nlp)

    # Create and train a vectorizer with a spacy tokenizer, with features
    # being word n-grams (and not letter n-grams)
    logger.info("Training vectorizer")
    vectorizer = TfidfVectorizer(tokenizer=t, analyzer="word", ngram_range=(1, 3))
    vectorizer.fit(corpus)
    # pickle.dump(vectorizer, open(cfg.vectorizer.format(language), "wb"))
    features = vectorizer.get_feature_names()
    logger.info("Vectorizer trained")

    return vectorizer, features


# TODO: merge into one function that takes as argument the scoring type?
def compute_climate_score(ngram_score_dict: Dict[str, float], pattern):
    # TODO: add documentation
    matching = Counter()
    scores = 0
    for ngram, score in ngram_score_dict.items():
        if re.match(pattern, ngram) is not None:
            scores += (len(ngram.split(" ")) * score)
            matching[ngram] += 1
    return scores, matching


def compute_shift_score(ngram_score_dict: Dict[str, float], pattern_weights_dict: Dict[str, float]):
    """
    Computes the Shift score.



    :param ngram_score_dict: Dictionary associating ngrams to a score.
    :param pattern_weights_dict: Dictionary associating patterns to weights.
    :return:
    """
    scores = 0.0
    matching = Counter()
    for ngram, score in ngram_score_dict.items():
        for pattern, weight in pattern_weights_dict.items():
            if re.match(pattern, ngram) is not None:
                # TODO: is this computation documented somewhere? where does it come from?
                scores += (len(ngram.split(" ")) * score) ** weight
                matching[ngram] += 1
    print(scores, matching)
    return scores, matching


def compute_sdg_scores(ngram_score_dict: Dict[str, float], sdgs_patterns):
    # SDG = Sustainable Development Goals
    # TODO: add documentation
    scores = {}
    for sdg, patterns in sdgs_patterns.items():
        if sum([re.match(pat, ngram) is not None for ngram, score in
                ngram_score_dict.items() for pat in patterns]) > 2:
            scores[sdg] = True
        else:
            scores[sdg] = False
    return scores
