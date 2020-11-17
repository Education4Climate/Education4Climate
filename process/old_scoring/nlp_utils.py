import re
def lemmatize(text,spacy_model):
    lemmas = [w.lemma_ for w in spacy_model(text) if not w.is_stop and w.pos_ != "PUNCT"]
    return lemmas


def comput_tfidf_score(index, model, bows, dictionary,patterns):
    scores = [x[1] ** (1 / patterns[p]) for x in model[bows[index]]
              for p in patterns.keys() if re.match(p, dictionary.get(x[0])) is not None]

    return sum(scores)