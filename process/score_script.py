import re,pandas as pd, numpy as np, random,json
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
    train=True

    if train:
        df = pd.read_json("../data/crawling-results/ucl_courses.json")
        print("resources loaded")
        df["text"] = df.content.astype(str) + "\n" + df.goal.astype(str) + "\n" + df.prerequisite.astype(str) + "\n" + df.theme
        df["text"] = df.content.astype(str) + "\n" + df.goal.astype(str) + "\n" + df.theme.astype(str)
        remove = ["«", "»", "/", "\\"]


        print(df["class"][0])

        #Construction/entrainement des modèles
        vectorizer=TfidfVectorizer(tokenizer=tokenize,analyzer="word",ngram_range=(1,4))
        vectorizer.fit(df.text.values.tolist())
        pickle.dump(vectorizer,open("../data/models/vectorizer.pkl","wb"))
        features=vectorizer.get_feature_names()
        print("vectorizer trained")
#        scaler=StandardScaler(with_mean=False)
#        X = scaler.fit_transform(sparse_matrix)
#        pickle.dump(scaler,open("../resources/scaler.pkl","wb"))
#        print(X.shape)
#        normalizer=Normalizer()
#        X=normalizer.fit_transform(X)
#        pickle.dump(normalizer,open("../resources/normalizer.pkl","wb"))
#        print("normalization done")
#        print(X.shape,type(X))
#        SVD=TruncatedSVD(n_components=200,algorithm='randomized', random_state=2019, n_iter=5)
#        #SVD.fit(matrix_sparse)
#        SVD.fit(X)
#        pickle.dump(SVD,open("../resources/svd.pkl","wb"))
#        print("reduction done")
#        #X_svd_reconst = SVD.inverse_transform(X_svd)
#
    else:
        vectorizer=pickle.load(open("../data/models/vectorizer.pkl","rb"))
        #scaler=pickle.load(open("../resources/scaler.pkl","rb"))
        #normalizer=pickle.load(open("../resources/normalizer.pkl","rb"))
        #SVD=pickle.load(open("../resources/svd.pkl","rb"))
        features=vectorizer.get_feature_names()
    print("models trained")
    df_patterns=pd.read_excel("../data/ODD/patterns_fr.xlsx",header=0)
    df_odd=df[["class","text"]].copy()
    scores=[]
    for odd in ["6"]:
        df_patterns["SDG{}_PATTERN".format(odd)]=df_patterns["SDG{}_PATTERN".format(odd)].apply(lambda x:refactor_pattern(x))
        patterns={r["SDG{}_PATTERN".format(odd)]:float(r["SDG{}_SCORE".format(odd)]) for i,r in df_patterns.iterrows()}

        for i,row in df_odd.iterrows():
            coo_kw=vectorizer.transform([row["text"]]).tocoo()
            words_text={features[idx]:score for idx,score in zip(coo_kw.col,coo_kw.data)}
            if i%1000==0: print(i)
            score=compute_score(words_text,patterns)
            scores.append(score)
    df_odd["score"]=scores

    df_odd.to_csv("../data/ucl_scoring.csv",index=False,encoding="utf-8")

