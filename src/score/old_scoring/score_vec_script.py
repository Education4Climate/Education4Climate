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
    return [unidecode(w.text.lower()) for w in nlp(text) if w.pos_ not in ["PUNCT","NUM","SYM","SPACE"] and w.is_stop is False and len(w.text)>2]
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
    df = pd.read_json("../../data/crawling-output/ucl_courses.json")
    print("resources loaded")
    df["text"] = df.content.astype(str) + "\n" + df.goal.astype(str) + "\n" + df.prerequisite.astype(
        str) + "\n" + df.theme
    df["text"] = df.content.astype(str) + "\n" + df.goal.astype(str) + "\n" + df.theme.astype(str)
    remove = ["«", "»", "/", "\\"]
    odds={odd:open("../data/ODD/{}.txt".format(odd)).read() for odd in ["6","12","13","14"]}
    if train:
        start=time.time()
        print(df["class"][0])
        corpus = [tokenize(text) for text in df.text.values.tolist()]
        for t in odds.values():corpus.append(tokenize(t))
        corpus = [TaggedDocument(doc, [i]) for i, doc in enumerate(corpus)]
        model = Doc2Vec(corpus, dm=1, window=4, vector_size=100, epochs=200)
        print("build model: ", timedelta(seconds=time.time() - start))
        size = model.wv.vector_size
        model.save("../data/models/dvec.bin")

    else:
        model = Doc2Vec.load("../data/models/dvec.bin")
    print("models trained")
    df_odd=df[["class","text"]].copy()
    df_odd=df_odd.dropna(subset=["text"])
    print(df_odd.shape,df_odd.columns)
    for odd,text_odd in odds.items():
        odd_vec=model.infer_vector(tokenize(text_odd))
        scores = []
        for i,text in enumerate(df_odd["text"].values.tolist()):
            vec_course=model.infer_vector(tokenize(text))
            if i%1000==0: print(i)
            score=cosine(odd_vec,vec_course)
            if not isinstance(score,float):score=0.0
            scores.append(score)
        df_odd["score_SDG_{}".format(odd)]=scores

    df_odd.to_csv("../data/ucl_scoring_vec.csv",index=False,encoding="utf-8")

