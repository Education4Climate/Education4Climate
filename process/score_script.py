import re,pandas as pd, numpy as np, random,json

import spacy
import pickle
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

    if train:


        print(df["class"][0])

        #Construction/entrainement des modèles
        vectorizer=TfidfVectorizer(tokenizer=tokenize,analyzer="word",ngram_range=(1,4))
        vectorizer.fit(df.text.values.tolist())
        pickle.dump(vectorizer,open("../data/models/vectorizer.pkl","wb"))
        features=vectorizer.get_feature_names()
        print("vectorizer trained")

    else:
        vectorizer=pickle.load(open("../data/models/vectorizer.pkl","rb"))
        features=vectorizer.get_feature_names()
    print("models trained")
    df_patterns=pd.read_excel("../data/ODD/patterns_fr.xlsx",header=0)
    df_odd=df[["class","text"]].copy()
    for odd in ["6","12","13","14"]:
        print("scoring odd {}".format(odd))
        scores = []
        df_patterns["SDG{}_PATTERN".format(odd)]=df_patterns["SDG{}_PATTERN".format(odd)].fillna("").apply(lambda x:refactor_pattern(x))
        patterns={r["SDG{}_PATTERN".format(odd)]:float(r["SDG{}_SCORE".format(odd)]) for i,r in df_patterns.iterrows() if len(r["SDG{}_PATTERN".format(odd)])>0}
        for i,row in df_odd.iterrows():
            coo_kw=vectorizer.transform([row["text"]]).tocoo()
            words_text={features[idx]:score for idx,score in zip(coo_kw.col,coo_kw.data)}
            if i%1000==0: print(i)
            score=compute_score(words_text,patterns)
            if not isinstance(score,float):score=0.0
            scores.append(score)
        df_odd["score_SDG_{}".format(odd)]=scores

    df_odd.to_csv("../data/ucl_scoring.csv",index=False,encoding="utf-8")

