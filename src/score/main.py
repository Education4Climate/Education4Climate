# -*- coding: utf-8 -*-

import argparse

import json
import pandas as pd

# from tqdm import tqdm  # Progress bar

from config.settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER
from utils import compute_score
# from utils import compute_shift_score, compute_sdg_scores, compute_climate_score, load_models,compute_score
# from patterns import get_sdg_patterns, get_shift_patterns, get_climate_patterns
LANGUAGES = ["fr"]  # ,"nl","en"]


def main(school: str, year: int, fields: str) -> None:
    """
    # TODO: update
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
    courses_df = courses_df[["id", "text"]].set_index("id")

    # Load patterns for different types of scores
    shift_patterns = json.load(open(f"../../data/patterns/shift_patterns.json"))
    climate_patterns = json.load(open(f"../../data/patterns/climate_patterns.json"))
    patterns_matches_dict = {"climate": {}, "shift": {}}
    for idx, text in courses_df.text.items():
        score, shift_patterns_matches_dict = compute_score(text, shift_patterns)
        courses_df.loc[idx, "shift_score"] = score
        if score == 1:
            patterns_matches_dict["shift"][idx] = shift_patterns_matches_dict
        score, climate_patterns_matches_dict = compute_score(text, climate_patterns)
        courses_df.loc[idx, "climate_score"] = score
        if score == 1:
            patterns_matches_dict["climate"][idx] = climate_patterns_matches_dict
    courses_df = courses_df.drop("text", axis=1)
    # Save scores
    output_fn = f"../../{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}.csv"
    print("Output file : {}".format(output_fn))
    courses_df.to_csv(output_fn, encoding="utf-8")
    # Save patterns
    with open(f"../../{SCORING_OUTPUT_FOLDER}{school}_matches_{year}.json", "w") as f:
        json.dump(patterns_matches_dict, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="School code")
    parser.add_argument("-y", "--year", help="Academic year", default=2020)
    parser.add_argument("-f", "--fields", default="content",
                        help="Specify the field(s) on which we compute the score."
                             " If several fields, they need to be separated by a ','")

    arguments = vars(parser.parse_args())
    main(**arguments)
