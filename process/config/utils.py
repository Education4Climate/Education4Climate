from unidecode import unidecode
from sklearn.feature_extraction.text import TfidfVectorizer

import spacy

def tokenize(text, nlp):
    return [unidecode(w.text.lower()) for w in nlp(text) if w.pos_ not in ["PUNCT","NUM","SYM","SPACE"] and w.is_stop is False]

def refactor_pattern(x):
    x=x.replace("\w+","[^ ]+").lower()
    x=unidecode(x)
    return x

def load_models(corpus, language):
    # Construction/entrainement des modeles
    nlp = spacy.load(language)
    print("training")
    vectorizer = TfidfVectorizer(tokenizer=tokenize, analyzer="word", ngram_range=(1, 3))
    vectorizer.fit(corpus)
    #pickle.dump(vectorizer, open(cfg.vectorizer.format(language), "wb"))
    features = vectorizer.get_feature_names()
    print("vectorizer trained")

    return vectorizer,features