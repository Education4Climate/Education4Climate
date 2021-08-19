# -*- coding: utf-8 -*-
from pathlib import Path
import argparse
from typing import List, Dict

import json
import pandas as pd

import langdetect
import re

from settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER

ACCEPTED_LANGUAGES = ["fr", "en", "nl"]


def compute_score(text: str, patterns: List[str]) -> (int, Dict[str, List[str]]):
    """
    Compare text to a list of patterns
    :param text: A string that has been lowerized
    :param patterns: List of patterns matching lowerized strings
    :return:
    - 1 if any pattern is find, 0 otherwise
    - a dictionary associating the patterns that matched to what they matched
    """

    pattern_matches_dict = {}
    score = 0
    for pattern in patterns:
        if isinstance(pattern, list):
            pattern_matches_dict["---".join(pattern)] = []
            matches = []
            # matches_text = []
            # check multi term matches
            t = ""
            for p in pattern:
                m = re.search(p, text)
                matches.append(m is not None)
                if m is not None:
                    start, end = m.span()
                    start = max(0, start - 20)
                    end = min(end + 20, len(text) - 1)
                    t += "---"
                    t += text[start:end]
            if False not in matches:
                score = 1
                pattern_matches_dict["---".join(pattern)] += [t]

        else:
            matches = list(re.finditer(pattern, text))
            if len(matches) != 0:
                score = 1
                pattern_matches_dict[pattern] = []
                for match in matches:
                    # For each match, retrieve a number of characters before and after to get the context
                    start, end = match.span()
                    start = max(0, start-20)
                    end = min(end+20, len(text)-1)
                    pattern_matches_dict[pattern] += [text[start:end]]
        pattern_matches_dict = {k: v for k, v in pattern_matches_dict.items() if len(v) > 0}

    return score, pattern_matches_dict


def main(school: str, year: int, fields: str) -> None:
    """
    Identifies for each course of a school whether they discuss a pre-defined set of thematics and saves the results.

    :param school: Code of the school whose courses will be scored.
    :param year: Year for which the scoring is done.
    :param fields: Data fields to be used for computing scores.

    :return: None
    """

    # Loading crawling results
    courses_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json")
    courses_df = pd.read_json(open(courses_fn, 'r'), dtype={'id': str})
    fields = fields.split(",")
    for field in fields:
        assert field in courses_df.columns, f"Error: the courses DataFrame doesn't contian a column {field}"
    # Drop courses for which the scoring field is empty
    courses_df = courses_df.dropna(subset=fields)
    # Concatenate the scoring fields
    courses_df["text"] = courses_df[fields].apply(lambda x: "\n".join(x.values), axis=1)
    courses_df = courses_df[["id", "languages", "text"]].set_index("id")

    # Load patterns for different types of scores
    themes_fn = Path(__file__).parent.absolute().joinpath("../../data/patterns/themes_patterns.json")
    themes_patterns = json.load(open(themes_fn, 'r'))
    themes = themes_patterns.keys()
    patterns_matches_dict = {theme: {} for theme in themes}
    for idx, text in courses_df.text.items():

        # Clean text
        text = text.lower()
        chars_to_replace = ["\r", "\t", "\n", "\xa0", ":", ";", ".", ",", "?", "!", "(", ")", "…"]
        for ch in chars_to_replace:
            text = text.replace(ch, " ")

        if len(text.strip(" ")) == 0:
            courses_df.loc[idx, themes] = 0
            continue

        # Detect language of text
        try:
            language = langdetect.detect(text)
        except langdetect.lang_detect_exception.LangDetectException:
            courses_df.loc[idx, themes] = 0
            continue

        # If we didn't identify a known language, use the first language in which the course is given
        if language not in ACCEPTED_LANGUAGES:
            print(idx, language)
            course_languages = list(set(courses_df.loc[idx, 'languages']).intersection(set(ACCEPTED_LANGUAGES)))
            if len(course_languages) > 0:
                language = course_languages[0]
                print(language)
            else:
                courses_df.loc[idx, themes] = 0
                continue

        # Match patterns and compute scores
        for theme in themes:
            score, shift_patterns_matches_dict = compute_score(text, themes_patterns[theme][language])
            courses_df.loc[idx, theme] = score
            if score == 1:
                patterns_matches_dict[theme][idx] = shift_patterns_matches_dict

    courses_df = courses_df.drop("text", axis=1)
    courses_df = courses_df.drop("languages", axis=1)
    courses_df = courses_df.astype(int)

    # Save scores
    output_fn = Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}.csv")
    courses_df.to_csv(output_fn, encoding="utf-8")
    # Save patterns
    matches_output_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_matches_{year}.json")
    with open(matches_output_fn, "w") as f:
        json.dump(patterns_matches_dict, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="School code")
    parser.add_argument("-y", "--year", help="Academic year", default=2020)
    parser.add_argument("-f", "--fields", default="name,content",
                        help="Specify the field(s) on which we compute the score."
                             " If several fields, they need to be separated by a ','")

    arguments = vars(parser.parse_args())
    main(**arguments)
