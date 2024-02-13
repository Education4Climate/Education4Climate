"""
Generation of the corpus
"""


import pandas as pd
import json
import os
from typing import List

from ast import literal_eval
from pathlib import Path

from settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER, CORPUS_FOLDER, YEAR, ACCEPTED_LANGUAGES


def generate_corpus(schools: List[str]):
    """
    Output an Excel file with one page per school, and for each course:
        - its id
        - its name
        - its url
        - the number of matched patterns
        - whether it is dedicated or not
        - the names of the patterns that matched
        - whether it has been checked by a human
        - the decision of the human, whether it should be kept in the corpus
        - the decision of the human, whether it should be considered dedicated
    """

    fn = Path(os.path.abspath('')).parent.absolute().joinpath(
                f"../{CORPUS_FOLDER}corpus.xlsx")

    # TODO: change everything that is under here
    with pd.ExcelWriter(fn) as writer:

        for school in schools:
            print(school)

            # Read matches file
            matches_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
                f"../{SCORING_OUTPUT_FOLDER}{school}_matches_{YEAR}.json")
            matches_json = json.load(open(matches_fn, 'r'))

            # Read score file
            scores_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
                f"../{SCORING_OUTPUT_FOLDER}{school}_courses_scoring_{YEAR}.csv")
            scores_df = pd.read_csv(scores_fn, dtype={'id': str}).set_index('id')
            scores_df['nb_matched_themes'] = scores_df[list(set(scores_df.columns) - {'dedicated'})].sum(axis=1)

            # Read course file to get course name
            courses_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
                f"../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{YEAR}.json")
            courses_df = pd.read_json(courses_fn, orient='records', dtype=str).set_index('id')[['name', 'url']]

            # Concatenate the different dataframes
            columns = ['nb_matched_patterns'] + ACCEPTED_LANGUAGES + \
                      ['checked', 'confirmed', 'dedicated confirmed', 'comment']
            empty_patterns_df = pd.DataFrame(index=courses_df.index, columns=columns)
            courses_df = pd.concat((courses_df, scores_df[['nb_matched_themes', 'dedicated']], empty_patterns_df), axis=1)
            courses_df['nb_matched_patterns'] = 0

            # For each matched courses in the matched dictionary, get the matched patterns in each language
            for courses_id_name in matches_json.keys():
                course_id = courses_id_name.split(':')[0]
                for lang in matches_json[courses_id_name].keys():
                    patterns = list(matches_json[courses_id_name][lang].keys())
                    courses_df.loc[course_id, lang] = " // ".join(patterns)
                    courses_df.loc[course_id, 'nb_matched_patterns'] += len(patterns)
            print(courses_df)

            # Write output
            courses_df.to_excel(writer, sheet_name=school)


if __name__ == "__main__":

    schools_df = pd.read_csv("/home/duboisa1/shifters/Education4Climate/data/schools.csv", index_col=0)
    schools_ = schools_df.index

    # schools_ = ['vub']

    generate_corpus(schools_)


