#!/usr/bin/python3.8
from langdetect import detect
import spacy
import os,time,sys
sys.path.append(os.path.abspath(os.getcwd()))
import re
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from unidecode import unidecode
import process.config as cfg
import pandas as pd
from collections import Counter


def tokenize(text):
    return [unidecode(w.text.lower()) for w in nlp(text) if w.pos_ not in ["PUNCT","NUM","SYM","SPACE"] and w.is_stop is False]

def refactor_pattern(x):
    x=x.replace("\w+","[^ ]+").lower()
    x=unidecode(x)
    return x

def compute_climate_score(words,pattern):
    matching=Counter()
    scores=0
    for word,score in words.items():
        if re.match(pattern,word) is not None:
            matching[word]+=1
            scores += (len(word.split(" ")) * score)
    return scores,matching

def compute_score(words,patterns):
    scores=0
    matching=Counter()
    for word,score in words.items():
        for pattern,weight in patterns.items():
            if re.match(pattern,word) is not None:
                scores += (len(word.split(" ")) * score) ** weight
                matching[word]+=1
    return scores,matching

def compute_odd_score(words,odds_patterns):
    scores={}
    for odd, patterns in odds_patterns.items():
        if sum([re.match(pat,w) is not None for w,score in words.items() for pat in patterns])>2:
            scores[odd]=True
        else: scores[odd]=False
    return scores


def load_models(corpus,language):
    # print(df["class"][0])
    # Construction/entrainement des modèles
    print("training")
    vectorizer = TfidfVectorizer(tokenizer=tokenize, analyzer="word", ngram_range=(1, 3))
    vectorizer.fit(corpus)
    #pickle.dump(vectorizer, open(cfg.vectorizer.format(language), "wb"))
    features = vectorizer.get_feature_names()
    print("vectorizer trained")

    return vectorizer,features


def get_pattern_shift(languages):
    patterns={}
    for language in languages:
        df_pattern_shift = pd.read_csv(cfg.pattern_sheets[language]["shift"], header=0)
        columns = list(df_pattern_shift.columns)
        df_pattern_shift = df_pattern_shift.dropna(subset=[columns[0]])
        df_pattern_shift[columns[-1]] = df_pattern_shift[columns[-1]].apply(lambda x: float(x.replace(",", ".")))
        pattern_shift = {refactor_pattern(pat): weight for pat, weight in zip(df_pattern_shift[columns[0]].values.tolist(), df_pattern_shift[columns[-1]].values.tolist())}
        patterns[language]=pattern_shift
    # df_pattern_shift[columns[0]]=df_pattern_shift[columns[0]].apply(lambda x:refactor_pattern(x))
    # df_pattern_shift.columns=["pattern","weight"]
    return patterns

def get_odd_patterns(languages):
    patterns={}
    for language in languages:
        df = pd.read_csv(cfg.pattern_sheets[language]["odd"],header=0)
        odds={}
        for col in df.columns:
            p=[refactor_pattern(x) for x in df[col].dropna().values.tolist()]
            odds[col]=p
        patterns[language]=odds
    return patterns

def get_climate_pattern(languages):
    patterns={}
    for language in languages:
        if "climate" in cfg.pattern_sheets[language].keys():
            tmp=pd.read_csv(cfg.pattern_sheets[language]["climate"],header=None)
            patterns[language]=tmp.iloc[0][0]
    return patterns

if __name__=="__main__":

    languages=["fr"]
    #nlp_models={lg:spacy.load(lg) for lg in languages}
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("-i","--input",help="input json file path")
    parser.add_argument("-o","--output",help="output xlsx file path",default="data/output.xlsx")
    parser.add_argument("-l","--language",help="specify language code",default="en")
    parser.add_argument("-f","--field",help="specify the field on which we compute the score",default="content,goal")

    args=parser.parse_args()

    language=args.language
    nlp=spacy.load(language)
    js=json.load(open(args.input))
    if isinstance(js,list):
        df = pd.DataFrame.from_dict(js)
    elif isinstance(js,dict):
        js=list(js.values())
        df=pd.DataFrame.from_dict(js)
    print("resources loaded")
    fields=args.field.split(",")
    df=df.dropna(subset=fields)
    df["text"] = df[fields].apply(lambda x : "\n".join(x.values),axis=1)
    remove = ["«", "»", "/", "\\"]
    df_courses=df[["shortname","url","class","text","teachers"]].copy()

    vectorizer,features=load_models(df_courses.text.values.tolist(),language)
    #load patterns for shift
    shift_patterns=get_pattern_shift(languages)
    climate_patterns=get_climate_pattern(languages)
    odd_patterns=get_odd_patterns(languages)
    results=[]
    for i, row in df_courses.iterrows():
        ##TODO##
        # implement handling of different languages when patterns are translated
        #try:
        #    detected_language=detect(row.text)
        #except :
            #print("error : ",row.text)
            #detected_language="fr"
        detected_language = "fr"
        # get tfidf_scores for ngrams in texts
        coo_kw = vectorizer.transform([row.text]).tocoo()
        words_text = {features[idx]: score for idx, score in zip(coo_kw.col, coo_kw.data)}

        if i % 1000 == 0: print(i)
        #compute scores
        score_shift,match_shift = compute_score(words_text, shift_patterns[detected_language])
        if not isinstance(score_shift, float): score_shift = 0.0
        score_climate,matching=compute_climate_score(words_text, climate_patterns[detected_language])

        data={"code":row.shortname,"shift_score":score_shift,"shiftpatterns": json.dumps(match_shift),"class":row["class"],"teachers":row.teachers}
        data["climate_score"]=score_climate
        data["climate_patterns"]=json.dumps(matching)
        #odd--scores  →  disabled
        odd_scores=compute_odd_score(words_text,odd_patterns[detected_language])
        for odd,b in odd_scores.items(): data[odd]=int(b)
        results.append(data)
    #write results to output file
    df_results=pd.DataFrame.from_dict(results)
    writer=pd.ExcelWriter(args.output)
    df_results.to_excel(writer,index=False,encoding="utf-8")
    writer.close()



