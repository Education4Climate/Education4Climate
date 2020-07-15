import re,pandas as pd, numpy as np, random,json
from gensim.models.doc2vec import Doc2Vec,TaggedDocument
from datetime import timedelta
import time
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.spatial.distance import cosine
import spacy
import pickle
from sklearn.preprocessing import StandardScaler,Normalizer
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from unidecode import unidecode


def tokenize(text):
    return [unidecode(w.text.lower()) for w in nlp(text) if w.pos_ not in ["PUNCT","NUM","SYM","SPACE"] and w.is_stop is False]
def refactor_pattern(x):
    x=x.replace("\w+","[^ ]+").lower()
    x=unidecode(x)
    return x

def compute_score(words,patterns):
    scores=0
    for word,score in words.items():
        for pattern,weight in patterns.items():
            if re.match(pattern,word) is not None:
                scores += (len(word.split(" ")) * score) ** weight
    return scores


if __name__=="__main__":

    nlp=spacy.load("fr")
    train=False
    df = pd.read_json("../data/crawling-results/ucl_courses.json")
    print("resources loaded")
    df["text"] = df.content.astype(str) + "\n" + df.goal.astype(str) + "\n" + df.prerequisite.astype(
        str) + "\n" + df.theme
    df["text"] = df.content.astype(str) + "\n" + df.goal.astype(str) + "\n" + df.theme.astype(str)
    remove = ["«", "»", "/", "\\"]
    odds=[]
    for odd in ["6","12","13","14"]:
        odds.append(open("../data/ODD/{}.txt".format(odd)).read())

    if train:
        start=time.time()
        print(df["class"][0])
        corpus = [tokenize(text) for text in df.text.values.tolist()]
        for t in odds:corpus.append(tokenize(t))
        corpus = [TaggedDocument(doc, [i]) for i, doc in enumerate(corpus)]
        model = Doc2Vec(corpus, dm=1, window=4, vector_size=100)
        print("build model: ", timedelta(seconds=time.time() - start))
        size = model.wv.vector_size
        model.save("../data/models/dvec.bin")

    else:
        model = Doc2Vec.load("../data/models/dvec.bin")
    print("models trained")
    df_odd=df[["class","text"]].copy()
    scores = []
    for odd in odds:

        for i,row in df_odd.iterrows():
            vec
            coo_kw=vectorizer.transform([row["text"]]).tocoo()
            words_text={features[idx]:score for idx,score in zip(coo_kw.col,coo_kw.data)}
            if i%1000==0: print(i)
            score=compute_score(words_text,patterns)
            if not isinstance(score,float):score=0.0
            scores.append(score)
        df_odd["score_SDG_{}".format(odd)]=scores

    df_odd.to_csv("../data/ucl_scoring.csv",index=False,encoding="utf-8")

