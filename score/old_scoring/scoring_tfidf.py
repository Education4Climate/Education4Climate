import pandas as pd
import os,sys,json
import spacy
sys.path.append(os.path.join(os.getcwd()))
import score.config.settings as cfg
from score.old_scoring.nlp_utils import lemmatize,comput_tfidf_score
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
import re
import numpy as np

def pattern_scoring(df):
    df["different_match"] = df[pattern_labels].apply(lambda x: (x != 0)).sum(axis=1)
    df["total_count"] = df[pattern_labels].sum(axis=1)
    df["score"] = df.total_count * df.different_match
    return df.sort_values("score",ascending=False)

def write_output(df,out_path,key_list):
    writer = pd.ExcelWriter(out_path)
    df[key_list].sort_values(by="score", ascending=False).to_excel(writer, index=None)
    writer.close()

def tfidf_scoring(df,patterns):
    dictionary = Dictionary(df.bigrams.values.tolist())
    bows = [dictionary.doc2bow(d) for d in df.bigrams.values.tolist()]
    model = TfidfModel(bows)

    df["tfidf_score"] = np.array([comput_tfidf_score(x, model, bows, dictionary,patterns) for x in range(df.shape[0])])
    return df.sort_values("tfidf_score",ascending=False)


#######################
#
#      Scoring score : gives a score expressing how much a text (i.e course) is related to global warming, sustainable developpement, etc (cfr. patterns)
#           2 possibilities: simple word count or tfidf weighted score
#######################
if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("input",help="input json file path")
    parser.add_argument("output",help="output xlsx file path",default="data/output.xlsx")
    parser.add_argument("-l","--language",help="specify language code",default="fr")
    parser.add_argument("-d","--debug",help="write all the pattern matches in the output file",action="store_true")
    parser.add_argument("--tfidf",help="compute a tfidf weighted score",action="store_true")

    args=parser.parse_args()

    nlp = spacy.load(args.language)
    #load data from json, build text feature and preprocess
    df=pd.read_json(args.input)
    df["text"] = df.content.astype(str) + "\n" + df.goal.astype(str) + \
                 "\n" + df.prerequisite.astype(str) + "\n" + df.theme
    df["lemmas"] = df.text.apply(lambda x:lemmatize(x,nlp))
    df["bigrams"] = df.lemmas.apply(lambda x: [" ".join(x[i:i + 2]).strip()
                                               for i in range(0, len(x)) if len(x[i:i + 1]) == 1])

    #load patterns
    patterns = json.load(open(cfg.patterns))[args.language]
    pattern_labels = [f'{p}_count' for p in patterns.keys()]
    for p, label in zip(patterns.keys(), pattern_labels):
        df[label] = df.bigrams.apply(lambda x: sum([(re.match(p, token) is not None) for token in x]) * patterns[p])
        df[label] += df.lemmas.apply(lambda x: sum([(re.match(p, token) is not None) for token in x]) * patterns[p])


    df=pattern_scoring(df)

    #if all matches are wanted in the output files :
    if args.debug:
        key_list = ["class"] + pattern_labels + ["total_count", "different_match", "score"]
    # write only essential information
    else:
        key_list = ["class","total_count", "different_match", "score"]
    if not args.tfidf: write_output(df,args.output,key_list)
    else:
        df=tfidf_scoring(df,patterns)
        key_list+=["tfidf_score"]
        write_output(df,args.output,key_list)
        print("succeeded")
