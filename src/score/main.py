# -*- coding: utf-8 -*-

import argparse

import json
import pandas as pd

from tqdm import tqdm  # Progress bar

from config.settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER
from utils import compute_shift_score, compute_sdg_score, compute_climate_score, load_models
from patterns import get_sdg_patterns, get_shift_patterns, get_climate_patterns


# TODO: need to document the scoring methodology in some exterior document
def main(school: str, year: int, fields: str, language: str) -> None:
    """
    Computes and saves a series of scores for each course that has non-empty 'fields' values.

    :param school: Code of the school whose courses will be scored.
    :param year: Year for which the scoring is done.
    # TODO: why should there be only one language in one given university?
    :param fields: Data fields to be used for computing scores.
    :param language: Code of the language in which the scoring fields are written.

    :return: None

    ----
    Note:
    Scores are first saved into a DataFrame before being saved. The keys of the DataFrame are the following:
    - shift_score:
    - shift_patterns:
    - climate_score:
    - climate_patterns:
    - 'sdg':

    """
    # TODO
    #  /!\ languages are fr, en, nl (related to sheets to be loaded in settings.py
    #  → use spacy download fr | en | nl  to avoid plain name of models (fr_core_news_sm)
    #  languages=["fr","en","fr"]

    # Load patterns for different types of scores
    # TODO: need to install that with pip?
    languages_dict = {"fr_core_news_sm": "fr"}  # , "en_core_web_sm": 'en'} # Commented for testing purpose
    languages = list(languages_dict.values())
    shift_patterns = get_shift_patterns(languages)
    # TODO: why is there no score in this case?
    climate_patterns = get_climate_patterns(languages)
    sdg_patterns = get_sdg_patterns(languages)
    print(shift_patterns)
    print(climate_patterns)
    print(sdg_patterns)
    exit()

    # Loading crawling results
    courses_fn = f"{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json"
    courses_df = pd.read_json(open(courses_fn, 'r'))
    fields = fields.split(",")
    # Drop courses for which the scoring field is empty
    # TODO: check that fields are existing in the dataframe
    courses_df = courses_df.dropna(subset=fields)
    # Concatenate the scoring fields
    courses_df["text"] = courses_df[fields].apply(lambda x: "\n".join(x.values), axis=1)
    courses_ds = courses_df[["id", "text"]].set_index("id").squeeze()

    # Loading models
    # TODO: can we delete this?
    # nlp_models = {lg: spacy.load(lg) for lg in languages}
    # TODO: this takes a shit load of time to load, normal?
    vectorizer, features = load_models(courses_df.text.values.tolist(), language)

    #results_df = pd.DataFrame(index=courses_df.index,
    #                          columns=["class", "shift_score", "shift_patterns", ""])
    results = []
    # TODO: voir si df_courses.apply() pourrait s'appliquer ici
    for idx, scoring_text in tqdm(courses_ds.items(), total=len(courses_ds)):
        # TODO: implement handling of different languages when patterns are translated
        # try:
        #    detected_language = detect(row.text)
        # except :
        # print("error : ",row.text)
        # detected_language = "fr"
        detected_language = "fr"
        # get tfidf_scores for ngrams in texts
        coo_kw = vectorizer.transform([scoring_text]).tocoo()
        words_text = {features[idx]: score for idx, score in zip(coo_kw.col, coo_kw.data)}

        # Computing scores
        score_shift, match_shift = compute_shift_score(words_text, shift_patterns[detected_language])
        if not isinstance(score_shift, float):
            score_shift = 0.0
        score_climate, matching = compute_climate_score(words_text, climate_patterns[detected_language])
        sdg_scores = compute_sdg_score(words_text, sdg_patterns[detected_language])

        # Generating data
        # TODO: why not save this directly in a DataFrame?
        data = {"id": idx,
                "shift_score": score_shift,
                "shift_patterns": json.dumps(match_shift),
                "climate_score": score_climate,
                "climate_patterns": json.dumps(matching)}
        for sdg, b in sdg_scores.items():
            data[sdg] = int(b)  # TODO Replace by literal statement

        results.append(data)

    # Writing results to output file
    df_results = pd.DataFrame.from_dict(results)
    output_fn = f"{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}.csv"
    df_results.to_csv(output_fn, index=False, encoding="utf-8")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="Input json file path")
    parser.add_argument("-y", "--year", help="Academic year", default=2020)
    # parser.add_argument("-i", "--input_fn", help="Input json file path")
    # parser.add_argument("-o", "--output_fn", help="Output xlsx file path", default="data/output.xlsx")
    parser.add_argument("-f", "--fields", default="content",
                        help="Specify the field(s) on which we compute the score."
                             " If several fields, they need to be separated by a ','")
    parser.add_argument("-l", "--language", help="Specify language code", default="fr_core_news_sm")

    arguments = vars(parser.parse_args())
    main(**arguments)
