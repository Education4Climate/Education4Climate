# -*- coding: utf-8 -*-

import argparse

import json
import pandas as pd

from tqdm import tqdm  # Progress bar

from config.settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER
from utils import compute_shift_score, compute_sdg_scores, compute_climate_score, load_models
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

    # Loading crawling results
    courses_fn = f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json"
    courses_df = pd.read_json(open(courses_fn, 'r'))
    fields = fields.split(",")
    for field in fields:
        assert field in courses_df.columns, f"Error: the courses DataFrame doesn't contian a column {field}"
    # Drop courses for which the scoring field is empty
    courses_df = courses_df.dropna(subset=fields)
    # Concatenate the scoring fields
    courses_df["text"] = courses_df[fields].apply(lambda x: "\n".join(x.values), axis=1)
    # TODO: remove limitation on length after testing is done
    courses_ds = courses_df[["id", "text"]].set_index("id").squeeze()[0:100]

    # Load patterns for different types of scores
    # TODO: need to install that with pip?
    languages_dict = {"fr_core_news_sm": "fr"}  # , "en_core_web_sm": 'en'} # Commented for testing purpose
    languages = list(languages_dict.values())
    shift_patterns = get_shift_patterns(languages)
    climate_patterns = get_climate_patterns(languages)
    sdg_patterns = get_sdg_patterns(languages)

    # Loading models
    # TODO: can we delete this?
    # nlp_models = {lg: spacy.load(lg) for lg in languages}
    # TODO: this takes a shit load of time to load, normal?
    vectorizer, features = load_models(courses_ds.tolist(), language)

    results_df = pd.DataFrame(index=courses_ds.index,
                              columns=["shift_score", "shift_patterns", "climate_score",
                                       "climate_patterns"] + [f"SDG{i}" for i in range(1, 18)])
    results = []
    # TODO: voir si df_courses.apply() pourrait s'appliquer ici
    for idx, scoring_text in tqdm(courses_ds.items(), total=len(courses_ds)):
        # TODO: implement handling of different languages when patterns are translated
        # try:
        #    detected_language = detect(row.text)
        # except :
        # print("error : ", row.text)
        # detected_language = "fr"
        detected_language = "fr"

        # TODO: why are we using tf-idf scores and not the binary?
        # Get tfidf_scores for ngrams in texts
        # TF-IDF means term-frequency times inverse document frequency
        # The higher the score the more 'relevant' the n-gram is
        # Transform text to tf-idf-weighted document-term matrix and convert te matrix to a coordinate format
        # This matrix contains one row per document (here equal to 1) and one column per feature
        tfidf_score_matrix = vectorizer.transform([scoring_text]).tocoo()
        feature_score_dict = {features[idx]: score for idx, score
                              in zip(tfidf_score_matrix.col, tfidf_score_matrix.data)}

        # Computing scores
        shift_score, shift_matching = compute_shift_score(feature_score_dict, shift_patterns[detected_language])
        # TODO: what is this? why wouldn't it be a float?
        if not isinstance(shift_score, float):
            shift_score = 0.0
        climate_score, climate_matching = compute_climate_score(feature_score_dict, climate_patterns[detected_language])
        sdg_scores = compute_sdg_scores(feature_score_dict, sdg_patterns[detected_language])

        # Saving results
        results_df.loc[idx, "shift_score"] = shift_score
        results_df.loc[idx, "shift_patterns"] = json.dumps(shift_matching)
        results_df.loc[idx, "climate_score"] = climate_score
        results_df.loc[idx, "climate_patterns"] = json.dumps(climate_matching)
        for sdg, sdg_score in sdg_scores.items():
            results_df.loc[idx, sdg] = sdg_score

    # Writing results to output file
    # TODO: remove _test when done testing
    output_fn = f"../../{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}_test2.csv"
    results_df.to_csv(output_fn, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="School code")
    parser.add_argument("-y", "--year", help="Academic year", default=2020)
    # parser.add_argument("-i", "--input_fn", help="Input json file path")
    # parser.add_argument("-o", "--output_fn", help="Output xlsx file path", default="data/output.xlsx")
    parser.add_argument("-f", "--fields", default="content",
                        help="Specify the field(s) on which we compute the score."
                             " If several fields, they need to be separated by a ','")
    parser.add_argument("-l", "--language", help="Specify language code", default="fr_core_news_sm")

    arguments = vars(parser.parse_args())
    main(**arguments)
