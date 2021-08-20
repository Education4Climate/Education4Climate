# -*- coding: utf-8 -*-
from pathlib import Path
import argparse
from typing import List
from os.path import isfile, isdir
from os import makedirs

import pandas as pd

from src.score.courses import score_school_courses
from settings import YEAR, CRAWLING_OUTPUT_FOLDER


def compare_dictionaries(dictionary1_name: str, dictionary2_name: str,
                         schools: List[str], year: int, fields: str):
    """
    Compute scores for a list of schools using two different dictionaries and compares the results

    :param dictionary1_name: Name of the first dictionary
    :param dictionary2_name: Name of the second dictionary
    :param schools: List of codes of schools for which the comparison is made
    :param year: Year for which the scoring is done
    :param fields: Data fields to be used for computing scores

    :notes:
    Both dictionaries are considered to be stored in data/patterns.
    Just the name of the file should be specified without the extension '.json'.

    The output of the scoring and of comparison is stored in data/dictionary-comparison
    """

    # Compute scores
    def compute_dictionary_score(output_dir, dictionary_name):
        if not isdir(output_dir):
            makedirs(output_dir)
        for school in schools:
            # Check whether the output file already exists
            if isfile(f"{output_dir}/{school}_scoring_{year}.csv"):
                continue
            print(f"Computing scores for school {school}")
            score_school_courses(school, year, fields, output_dir, dictionary_name)

    print(f"Computing scores for dictionary {dictionary1_name}\n--------------------------------")
    output_dir_1 = str(
        Path(__file__).parent.absolute().joinpath(f"../../data/dictionary-comparison/{dictionary1_name}"))
    compute_dictionary_score(output_dir_1, dictionary1_name)
    print("All schools done\n")

    print(f"Computing scores for dictionary {dictionary2_name}\n--------------------------------")
    output_dir_2 = str(
        Path(__file__).parent.absolute().joinpath(f"../../data/dictionary-comparison/{dictionary2_name}"))
    compute_dictionary_score(output_dir_2, dictionary2_name)
    print("All schools done\n")

    # Loading results for all schools
    def get_results(output_dir):

        results_df = pd.DataFrame(columns=["university", "id", "name"])
        for school in schools:

            # Load scores
            courses_scores_ds = pd.read_csv(f"{output_dir}/{school}_scoring_{year}.csv",
                                            dtype={'id': str}).set_index("id")
            # Keep only courses with a positive score
            courses_scores_ds = courses_scores_ds[courses_scores_ds.sum(axis=1) > 0]

            # Load data
            courses_fn = \
                Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json")
            courses_df = pd.read_json(open(courses_fn, 'r'), dtype={'id': str}).set_index("id")
            courses_df = courses_df.loc[courses_scores_ds.index, "name"]

            # Add to the main dataframe
            courses_df = pd.DataFrame({"university": pd.Series([school]*len(courses_df), dtype=str),
                                       "id": courses_df.index,
                                       "name": courses_df.values}, dtype=str)
            results_df = pd.concat((results_df, courses_df), axis=0)

        return results_df

    d1_results = get_results(output_dir_1)
    d2_results = get_results(output_dir_2)

    # Compare the results
    common_courses = set(d1_results.id).intersection(set(d2_results.id))
    added_courses_in_d2 = set(d2_results.id).difference(set(d1_results.id))
    removed_courses_in_d2 = set(d1_results.id).difference(set(d2_results.id))

    # Save results
    fn = Path(__file__).parent.absolute().joinpath(f"../../data/dictionary-comparison/"
                                                   f"{dictionary1_name}_to_{dictionary2_name}.xlsx")
    with pd.ExcelWriter(fn) as writer:
        d1_results[d1_results.id.isin(common_courses)].to_excel(writer, sheet_name="Common courses", index=False)
        d2_results[d2_results.id.isin(added_courses_in_d2)]\
            .to_excel(writer, sheet_name="Courses added by dictionary 2", index=False)
        d1_results[d1_results.id.isin(removed_courses_in_d2)]\
            .to_excel(writer, sheet_name="Courses removed by dictionary 2", index=False)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-d1", "--dictionary1_name", help="Name of the first dictionary")
    parser.add_argument("-d2", "--dictionary2_name", help="Name of the second dictionary")
    parser.add_argument("-y", "--year", help="Academic year", default=YEAR)
    # TODO: this will need to change if use different fields for each school ==> need to create a file for this
    parser.add_argument("-f", "--fields", default="name,content",
                        help="Specify the field(s) on which we compute the score."
                             " If several fields, they need to be separated by a ','")

    # TODO: add kuleuven, uantwerp, uclouvain
    schools = ["ugent", "uhasselt", "ulb", "uliege", "umons", "unamur", "uslb", "vub"]

    arguments = vars(parser.parse_args())
    arguments['schools'] = schools
    compare_dictionaries(**arguments)
