# -*- coding: utf-8 -*-

import argparse

import json
import pandas as pd

import langdetect

from config.settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER
from utils import compute_score

ACCEPTED_LANGUAGES = ["fr"]  # ["en", "fr", "nl"]


def main(school: str, year: int, fields: str) -> None:
    """
    # TODO: update
    Computes and saves a series of scores for each course that has non-empty 'fields' values.

    :param school: Code of the school whose courses will be scored.
    :param year: Year for which the scoring is done.
    :param fields: Data fields to be used for computing scores.

    :return: None


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
    themes_patterns = json.load(open(f"../../data/patterns/themes_patterns.json"))
    themes = themes_patterns.keys()
    patterns_matches_dict = {theme: {} for theme in themes}
    for idx, text in courses_df.text.items():

        # Clean text # TODO: maybe a better way to do that
        text = text.lower()
        for ch in ["\r", "\t", "\n", "\xa0", ":", ";", ".", ",", "?", "!", "(", ")", "…"]:
            text = text.replace(ch, " ")

        if len(text) == 0:
            courses_df.loc[idx, themes] = 0
            continue

        # Detect language of text
        language = langdetect.detect(text)
        # TODO: create patterns for 'en' and 'nl'
        if language not in ACCEPTED_LANGUAGES:
            print(idx, language)
            courses_df.loc[idx, themes] = 0
            continue

        # Match patterns and compute scores
        for theme in themes:
            score, shift_patterns_matches_dict = compute_score(text, themes_patterns[theme][language])
            courses_df.loc[idx, theme] = score
            if score == 1:
                patterns_matches_dict[theme][idx] = shift_patterns_matches_dict

    courses_df = courses_df.drop("text", axis=1)
    courses_df = courses_df.astype(int)

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
