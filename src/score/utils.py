# -*- coding: utf-8 -*-

from unidecode import unidecode
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from functools import partial

from collections import Counter
import re

import logging
logger = logging.Logger(name='Utils Logger')


def load_models(corpus, language):
    # Construction/entrainement des modeles
    nlp = spacy.load(language)
    logger.info("Training vectorizer")

    def tokenize(nlp, text):
        return [unidecode(w.text.lower()) for w in nlp(text)
                if w.pos_ not in ["PUNCT", "NUM", "SYM", "SPACE"] and w.is_stop is False]
    t = partial(tokenize, nlp)  # Moyen d'envoyer un argument (nlp) dans une fonction callback
    vectorizer = TfidfVectorizer(tokenizer=t, analyzer="word", ngram_range=(1, 3))
    vectorizer.fit(corpus)
    # pickle.dump(vectorizer, open(cfg.vectorizer.format(language), "wb"))
    features = vectorizer.get_feature_names()
    logger.info("Vectorizer trained")

    return vectorizer, features


# TODO: merge into one function that takes as argument the scoring type?
def compute_climate_score(words, pattern):
    # TODO: add documentation
    matching = Counter()
    scores = 0
    for word, score in words.items():
        if re.match(pattern, word) is not None:
            matching[word] += 1
            scores += (len(word.split(" ")) * score)
    return scores, matching


def compute_shift_score(words, patterns):
    # TODO: add documentation
    scores = 0
    matching = Counter()
    for word, score in words.items():
        for pattern, weight in patterns.items():
            if re.match(pattern, word) is not None:
                scores += (len(word.split(" ")) * score) ** weight
                matching[word] += 1
    return scores, matching


def compute_sdg_score(words, sdgs_patterns):
    # SDG = Sustainable Development Goals
    # TODO: add documentation
    scores = {}
    for sdg, patterns in sdgs_patterns.items():
        if sum([re.match(pat, w) is not None for w, score in words.items() for pat in patterns]) > 2:
            scores[sdg] = True
        else:
            scores[sdg] = False
    return scores
