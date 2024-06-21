# -*- coding: utf-8 -*-
from pathlib import Path
import argparse
from typing import List, Dict

import json
import pandas as pd
from ast import literal_eval
from unidecode import unidecode

import langdetect
from langdetect import DetectorFactory
import re

import threading
from tqdm import tqdm

from settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER, ACCEPTED_LANGUAGES

DetectorFactory.seed = 0


def compute_score(text: str, patterns_themes_df: pd.DataFrame) -> (int, Dict[str, List[str]]):
    """
    Compare text to a list of patterns
    :param text: A string that has been lowered
    :param patterns_themes_df: DataFrame containing all patterns in first column
    and corresponding themes in second column
    :return:
    - 1 if any pattern is find, 0 otherwise
    - a list of the themes that matched
    - a dictionary associating the patterns that matched to what they matched
    """

    pattern_matches_dict = {}
    score = 0
    matched_themes = set()
    for _, (pattern, themes) in patterns_themes_df.iterrows():

        # Multi-pattern
        if pattern.startswith("["):

            sub_patterns = pattern[1:-1].split(", ")
            # Check if all patterns in multi-pattern expression match
            pattern_score = 1
            patterns_matches_list = []
            for sub_pattern in sub_patterns:

                matches = list(re.finditer(sub_pattern, text))
                # If there are no matches for a pattern stop the search
                if len(matches) == 0:
                    pattern_score = 0
                    break
                for match in matches:
                    # For each match, retrieve a number of characters before and after to get the context
                    start, end = match.span()
                    start = max(0, start-20)
                    end = min(end+20, len(text)-1)
                    patterns_matches_list += [text[start:end]]

            if pattern_score != 0:
                score = 1
                matched_themes |= set(themes)
                pattern_matches_dict[pattern] = patterns_matches_list

        # Single pattern
        else:
            matches = list(re.finditer(pattern, text))
            if len(matches) != 0:
                score = 1
                matched_themes |= set(themes)
                pattern_matches_dict[pattern] = []
                for match in matches:
                    # For each match, retrieve a number of characters before and after to get the context
                    start, end = match.span()
                    start = max(0, start-20)
                    end = min(end+20, len(text)-1)
                    pattern_matches_dict[pattern] += [text[start:end]]

        pattern_matches_dict = {k: v for k, v in pattern_matches_dict.items() if len(v) > 0}

    return score, list(matched_themes), pattern_matches_dict


def clean_text(text: str):
    text = unidecode(text).lower()
    chars_to_replace = ["\r", "\t", "\n", "\xa0", ":", ";", ".", ",", "?", "!", "(", ")", "…", "'"]
    for ch in chars_to_replace:
        text = text.replace(ch, " ")
    return text


def score_school_courses(school: str, year: int, output_dir: str, dictionary_name: str,
                         run_file_path: str, run_nb: int = 1) -> None:
    """
    Identifies for each course of a school whether they discuss a pre-defined set of thematics and saves the results.

    :param school: Code of the school whose courses will be scored.
    :param year: Year for which the scoring is done.
    :param output_dir: Name of the main directory where the results should be saved
    :param dictionary_name: Name of the dictionary that should be used to score the courses without the extnsion '.json'
    :param run_file_path: Path to file where the main code is executed
    :param run_nb: int used for displaying the advancement of runs

    :return: None
    """

    # Loading crawling results
    courses_fn = \
        Path(run_file_path).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json")
    courses_df = pd.read_json(open(courses_fn, 'r'), dtype={'id': str})

    # Load fields on which the scoring has to be done
    scoring_fields_fn = Path(run_file_path).parent.absolute().joinpath(f"../../data/scoring_fields.csv")
    fields = ["name"] + pd.read_csv(scoring_fields_fn, index_col=0).loc[school, 'fields'].split(";")
    for field in fields:
        assert field in courses_df.columns, f"Error: the courses DataFrame doesn't contain a column {field}"
        # Convert Nans to "
        courses_df[field] = courses_df[field].apply(lambda x: "" if x is None else x)

    # Concatenate the scoring fields
    courses_df["scoring_text"] = courses_df[fields].apply(lambda x: clean_text(" ".join(x.values)), axis=1)
    courses_df["full_text"] = courses_df[["name", "content", "goal", "activity", "other"]]\
        .apply(lambda x: clean_text(" ".join(x.values)), axis=1)
    courses_df = courses_df[["id", "languages", "name", "scoring_text", "full_text"]].set_index("id")

    # Load patterns for different types of scores
    patterns_dict = {}
    themes = []
    for lang in ACCEPTED_LANGUAGES:
        themes_fn = Path(run_file_path).parent.absolute().joinpath(f"../../data/patterns/{dictionary_name}/{lang}.csv")
        lang_patterns_df = pd.read_csv(themes_fn, converters={'themes': literal_eval})
        patterns_dict[lang] = lang_patterns_df
        themes = set(themes).union(set(lang_patterns_df["themes"].sum()))
    themes = sorted(list(themes))

    # Dedicated patterns
    dedicated_patterns_dict = {}
    for lang in ACCEPTED_LANGUAGES:
        themes_fn = Path(run_file_path).parent.absolute().joinpath(f"../../data/patterns/dedicated/{lang}.csv")
        dedicated_patterns_dict[lang] = pd.read_csv(themes_fn, converters={'themes': literal_eval})

    patterns_matches_dict = {}
    scores_df = pd.DataFrame(0, index=courses_df.index, columns=themes + ["dedicated"], dtype=int)

    with tqdm(total=len(courses_df), desc=f"{school}", position=run_nb) as pbar:  # Each task has its own progress bar
        for i, (idx, name, scoring_text, full_text) \
                in courses_df.reset_index()[["id", "name", "scoring_text", "full_text"]].iterrows():

            # scoring_text = clean_text(scoring_text)
            # full_text = clean_text(full_text)

            # if i % 100 == 0:
            #     print(f"{i}/{len(courses_df.index)}")

            if len(scoring_text.strip(" ")) == 0:
                continue

            # Detect language of text using full_text
            try:
                languages = [l.lang for l in langdetect.detect_langs(full_text)]
            except langdetect.lang_detect_exception.LangDetectException:
                print("Exception detected")
                courses_df.loc[idx, themes] = 0
                continue

            # If we didn't identify a language for which we have a dictionary
            # use the first language in which the course is given
            languages = [l for l in languages if l in ACCEPTED_LANGUAGES]
            if len(languages) == 0:
                languages = list(set(courses_df.loc[idx, 'languages']).intersection(set(ACCEPTED_LANGUAGES)))
                if len(languages) == 0:
                    continue

            # Match patterns and compute scores
            for language in languages:
                score, matched_themes, shift_patterns_matches_dict = \
                    compute_score(scoring_text, patterns_dict[language])
                scores_df.loc[idx, matched_themes] |= score
                if score == 1:
                    patterns_matches_dict[f"{idx}: {name}"] = {}
                    patterns_matches_dict[f"{idx}: {name}"][language] = shift_patterns_matches_dict
                    # Check if course is dedicated
                    if any([re.search(p, clean_text(name)) is not None
                            for p in dedicated_patterns_dict[language]["patterns"]]):
                        scores_df.loc[idx, "dedicated"] |= 1

            if i % 100 == 99:
                pbar.update(100)  # Increment the progress bar

        # Save scores
        # TODO: change add -test for the francois test
        output_fn = f"{output_dir}/{school}_courses_scoring_{year}.csv"
        scores_df.to_csv(output_fn, encoding="utf-8")
        # Save patterns
        # TODO: change add -test for the francois test
        matches_output_fn = f"{output_dir}/{school}_matches_{year}.json"
        with open(matches_output_fn, "w") as f:
            json.dump(patterns_matches_dict, f, indent=4)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="School code")
    parser.add_argument("-y", "--year", help="Academic year", default=2023)

    arguments = vars(parser.parse_args())
    arguments['output_dir'] = Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}/")
    arguments['dictionary_name'] = 'v2.0'

    schools_ = ["kuleuven", "uantwerpen", "ugent", "uhasselt", "vub"]
    schools_ += ["artevelde", "ehb", "hogent", "howest", "odisee", "thomasmore", "ucll", "vives"]

    schools_ = ['uantwerpen']
    # schools_ = ["uclouvain", "ulb", "uliege", "umons", "unamur", "uslb"]
    # schools_ += ["ecam", "ecsedi-isalt", "he-ferrer", "heaj", "hech", "hel", "heldb", "helmo",
    #              "henallux", "hepl", "hers", "ichec", "ihecs", "ispg", "issig", "vinci"]

    arguments['run_file_path'] = __file__

    threads = []
    for i, school in enumerate(schools_):
        arguments['school'] = school
        arguments['run_nb'] = i
        print(school)
        thread = threading.Thread(target=score_school_courses, kwargs=arguments)
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for t in threads:
        t.join()
