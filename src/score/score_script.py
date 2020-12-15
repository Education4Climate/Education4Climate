# -*- coding: utf-8 -*-

from tqdm import tqdm  # Progress bar

import re
import json

import config.settings as s
import config.utils as u

import pandas as pd
from collections import Counter


# -------------------------- SCORE COMPUTING --------------------------------

def compute_climate_score(words, pattern):
    matching = Counter()
    scores = 0
    for word, score in words.items():
        if re.match(pattern, word) is not None:
            matching[word] += 1
            scores += (len(word.split(" ")) * score)
    return scores, matching


def compute_score(words, patterns):
    scores = 0
    matching = Counter()
    for word, score in words.items():
        for pattern, weight in patterns.items():
            if re.match(pattern, word) is not None:
                scores += (len(word.split(" ")) * score) ** weight
                matching[word] += 1
    return scores, matching


def compute_odd_score(words, odds_patterns):
    scores = {}
    for odd, patterns in odds_patterns.items():
        if sum([re.match(pat, w) is not None for w, score in words.items() for pat in patterns]) > 2:
            scores[odd] = True
        else:
            scores[odd] = False
    return scores


# -------------------------- PATTERNS LOADING --------------------------------

def get_shift_patterns(languages):
    patterns = {}
    for language in languages:
        print('{}'.format(s.PATTERN_SHEETS))
        df_pattern_shift = pd.read_csv(s.PATTERN_SHEETS[language]["shift"], header=0)
        columns = list(df_pattern_shift.columns)
        df_pattern_shift = df_pattern_shift.dropna(subset=[columns[0]])
        df_pattern_shift[columns[-1]] = df_pattern_shift[columns[-1]].apply(lambda x: float(x.replace(",", ".")))
        pattern_shift = {u.refactor_pattern(pat): weight for pat, weight in
                         zip(df_pattern_shift[columns[0]].values.tolist(),
                             df_pattern_shift[columns[-1]].values.tolist())}
        patterns[language] = pattern_shift
    # df_pattern_shift[columns[0]]=df_pattern_shift[columns[0]].apply(lambda x:refactor_pattern(x))
    # df_pattern_shift.columns=["pattern","weight"]
    return patterns


def get_odd_patterns(languages):
    patterns = {}
    for language in languages:
        df = pd.read_csv(s.PATTERN_SHEETS[language]["odd"],header=0)
        odds={}

        for col in df.columns:
            p = [u.refactor_pattern(x) for x in df[col].dropna().values.tolist()]
            odds[col] = p
        patterns[language] = odds
    return patterns


def get_climate_patterns(languages):
    patterns = {}
    for language in languages:
        if "climate" in s.PATTERN_SHEETS[language].keys():
            tmp=pd.read_csv(s.PATTERN_SHEETS[language]["climate"],header=None)
            patterns[language]=tmp.iloc[0][0]
    return patterns


# -------------------------- MAIN --------------------------------

def main(args):
    # TODO
    # /!\ languages are fr, en, nl (related to sheets to be loaded in settings.py
    # → use spacy download fr | en | nl  to avoid plain name of models (fr_core_news_sm)
    # languages=["fr","en","fr"]
    languages = {"fr_core_news_sm": "fr"}  # , "en_core_web_sm": 'en'} # Commented for testing purpose

    # nlp_models={lg:spacy.load(lg) for lg in languages}

    # Loading crawling results
    js = json.load(open(args.input))
    if isinstance(js, list):
        df = pd.DataFrame.from_dict(js)
    elif isinstance(js, dict):
        js = list(js.values())
        df = pd.DataFrame.from_dict(js)
    print("Crawled courses loaded")
    fields = args.field.split(",")
    df = df.dropna(subset=fields)
    df["text"] = df[fields].apply(lambda x: "\n".join(x.values), axis=1)
    df_courses = df[["id", "url", "name", "text", "teacher"]].copy()

    # Loading models
    language = args.language
    vectorizer, features = u.load_models(df_courses.text.values.tolist(), language)

    # Load patterns for different scores
    shift_patterns = get_shift_patterns(languages.values())
    climate_patterns = get_climate_patterns(languages.values())
    odd_patterns = get_odd_patterns(languages.values())

    results = []
    print(df_courses)

    for i, row in tqdm(df_courses.iterrows(),
                       total=df_courses.shape[0]):  # TODO: voir si df_courses.apply() pourrait s'appliquer ici
        # TODO
        # implement handling of different languages when patterns are translated
        # try:
        #    detected_language=detect(row.text)
        # except :
        # print("error : ",row.text)
        # detected_language="fr"
        detected_language = "fr"
        # get tfidf_scores for ngrams in texts
        coo_kw = vectorizer.transform([row.text]).tocoo()
        words_text = {features[idx]: score for idx, score in zip(coo_kw.col, coo_kw.data)}

        # if i % 1000 == 0: print(i)  # TODO: Replace by progressbar

        # Computing scores
        score_shift, match_shift = compute_score(words_text, shift_patterns[detected_language])
        if not isinstance(score_shift, float):
            score_shift = 0.0
        score_climate, matching = compute_climate_score(words_text, climate_patterns[detected_language])
        odd_scores = compute_odd_score(words_text, odd_patterns[detected_language])

        # Generating data
        data = {"code": row.id,
                "shift_score": score_shift,
                "shiftpatterns": json.dumps(match_shift),
                "class": row.name,
                "teachers": row.teacher,
                "climate_score": score_climate,
                "climate_patterns": json.dumps(matching)}
        for odd, b in odd_scores.items():
            data[odd] = int(b)  # TODO Replace by literal statement

        results.append(data)

    # Writing results to output file
    df_results = pd.DataFrame.from_dict(results)
    df_results.to_csv(args.output, index=False, encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input json file path")
    parser.add_argument("-o", "--output", help="output xlsx file path", default="data/output.xlsx")
    parser.add_argument("-l", "--language", help="specify language code", default="fr_core_news_sm")
    parser.add_argument("-f", "--field", help="specify the field on which we compute the score", default="content,goal")

    arguments = parser.parse_args()
    main(arguments)
