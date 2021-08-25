# -*- coding: utf-8 -*-
from pathlib import Path
import argparse
from typing import List, Dict

import json
import pandas as pd

import langdetect
from langdetect import DetectorFactory, detect
import re

from settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER

# Languages for which a dictionary is defined
ACCEPTED_LANGUAGES = ["fr", "en", "nl"]
DetectorFactory.seed = 0


def compute_score(text: str, patterns: List[str]) -> (int, Dict[str, List[str]]):
    """
    Compare text to a list of patterns
    :param text: A string that has been lowered
    :param patterns: List of patterns matching lowered strings
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


def score_school_courses(school: str, year: int, fields: str, output_dir: str,
                         dictionary_name: str = 'themes_patterns') -> None:
    """
    Identifies for each course of a school whether they discuss a pre-defined set of thematics and saves the results.

    :param school: Code of the school whose courses will be scored.
    :param year: Year for which the scoring is done.
    :param fields: Data fields to be used for computing scores.
    :param output_dir: Name of the main directory where the results should be saved
    :param dictionary_name: Name of the dictionary that should be used to score the courses without the extnsion '.json'.

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
    courses_df["scoring_text"] = courses_df[fields].apply(lambda x: "\n".join(x.values), axis=1)
    courses_df["full_text"] = courses_df[["name", "content", "goal", "activity", "other"]]\
        .apply(lambda x: "\n".join(x.values), axis=1)
    courses_df = courses_df[["id", "languages", "scoring_text", "full_text"]].set_index("id")

    # Load patterns for different types of scores
    themes_fn = Path(__file__).parent.absolute().joinpath(f"../../data/patterns/{dictionary_name}.json")
    themes_patterns = json.load(open(themes_fn, 'r'))
    themes = themes_patterns.keys()
    patterns_matches_dict = {theme: {} for theme in themes}
    scores_df = pd.DataFrame(0, index=courses_df.index, columns=themes, dtype=int)
    for idx, (scoring_text, full_text) in courses_df[["scoring_text", "full_text"]].iterrows():

        # Clean texts
        def clan_text(text):
            text = text.lower()
            chars_to_replace = ["\r", "\t", "\n", "\xa0", ":", ";", ".", ",", "?", "!", "(", ")", "…"]
            for ch in chars_to_replace:
                text = text.replace(ch, " ")
            return text
        scoring_text = clan_text(scoring_text)
        full_text = clan_text(full_text)

        if len(scoring_text.strip(" ")) == 0:
            continue

        # Detect language of text using full_text
        try:
            languages = [l.lang for l in langdetect.detect_langs(full_text)]
        except langdetect.lang_detect_exception.LangDetectException:
            print("Exception detected")
            courses_df.loc[idx, themes] = 0
            continue

        # If we didn't identify a language for which we have a dictionary,
        # use the first language in which the course is given
        languages = [l for l in languages if l in ACCEPTED_LANGUAGES]
        if len(languages) == 0:
            languages = list(set(courses_df.loc[idx, 'languages']).intersection(set(ACCEPTED_LANGUAGES)))
            if len(languages) == 0:
                continue

        # Match patterns and compute scores
        for theme in themes:
            for language in languages:
                score, shift_patterns_matches_dict = compute_score(scoring_text, themes_patterns[theme][language])
                scores_df.loc[idx, theme] |= score
                if score == 1:
                    patterns_matches_dict[theme][idx] = {}
                    patterns_matches_dict[theme][idx][language] = shift_patterns_matches_dict

    # Save scores
    output_fn = f"{output_dir}/{school}_scoring_{year}.csv"
    scores_df.to_csv(output_fn, encoding="utf-8")
    # Save patterns
    matches_output_fn = f"{output_dir}/{school}_matches_{year}.json"
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
    arguments['output_dir'] = Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}/")
    score_school_courses(**arguments)
