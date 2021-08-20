# -*- coding: utf-8 -*-
from pathlib import Path
import argparse
from typing import List

import configargparse

from src.score.courses import score_school_courses


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
    Just the name of the file should be specified.

    The output of the scoring and of comparison is stored in data/dictionary-comparison

    TODO:
     - Open the two dictionaries
     - Check if scoring has not already been done (need to check all schools)
     - Compute scores for the dictionaries for which it is not the case
     - Get for both dictionaries, the list of courses that have a score > 1
     - Compute difference in sets
     - Save the results to an excel file with 3 sheets: courses that have scored with both dictionaries,
       courses that have been added using dictionary 2, and courses that have been removed using dictionary 2
       For each sheets, 3 columns: university, code, name (+ matching patterns?)

    """

    # Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}")

    return


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-d1", "--dictionary1_name", help="Name of the first dictionary")
    parser.add_argument("-d2", "--dictionary1_name", help="Name of the second dictionary")
    parser.add_argument("-y", "--year", help="Academic year", default=2020)
    # TODO: this will need to change if use different fields for each school ==> need to create a file for this
    parser.add_argument("-f", "--fields", default="name,content",
                        help="Specify the field(s) on which we compute the score."
                             " If several fields, they need to be separated by a ','")

    schools = ["kuleuven", "uantwerpen", "uclouvain", "ugent", "uhasselt",
               "ulb", "uliege", "umons", "unamur", "uslb", "vub"]

    arguments = vars(parser.parse_args())
    arguments['schools'] = schools
    compare_dictionaries(**arguments)
