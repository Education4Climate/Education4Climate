from pathlib import Path
import argparse

import numpy as np
import pandas as pd

from settings import CRAWLING_OUTPUT_FOLDER


def merge_programs(school: str, year: int):
    """
    Merge duplicated programs.

    :param school: Code of the school whose programs will be merged.
    :param year: Year for which the data was crawled.

    :return: None

    Note:
    After running unicrawl/spiders/{school}_programs.py, programs can be split over several lines
     (due to the way the website is organised. The goal of this function is to merge those lines
     to have one line per program
    """

    # Read the programs file
    programs_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_programs_{year}_pre.json")
    programs_df = pd.read_json(programs_fn).set_index("id")

    # Group different keys
    programs_df_grouped = programs_df.groupby("id")
    programs_merged_df = programs_df_grouped["name"].unique().apply(lambda x: x[0]).to_frame()
    for key in ['cycle', 'url']:
        programs_merged_df[key] = programs_df_grouped[key].unique().apply(lambda x: x[0])
    keys_as_list_to_set = ['faculties', 'campuses']
    for key in keys_as_list_to_set:
        programs_merged_df[key] = programs_df_grouped[key].sum().apply(lambda x: list(set(x)))
    keys_as_list = ['courses', 'ects']
    for key in keys_as_list:
        programs_merged_df[key] = programs_df_grouped[key].sum()

    # Remove duplicate courses
    def remove_doubles(x):
        courses, positions = np.unique(x.courses, return_index=True)
        x.courses = list(courses)
        for key in keys_as_list[1:]:  # Change ects
            x[key] = list(np.array(x[key])[positions])
        return x

    if (school,year)==('uclouvain','2023'):
        programs_merged_df.at['IEJB2FC','ects']=[0,8,8,3]
        programs_merged_df.at['METB2FC','ects']=[0,0,0,0,0,0,10]
        
    programs_merged_df[keys_as_list] = programs_merged_df[keys_as_list].apply(lambda x: remove_doubles(x), axis=1)

    programs_merged_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_programs_{year}.json")
    programs_merged_df.reset_index().to_json(programs_merged_fn, orient='records', indent=1)


def merge_courses(school: str, year: int):
    """
    Merge duplicated courses.

    :param school: Code of the school whose courses will be merged.
    :param year: Year for which the data was crawled.

    :return: None

    Note:
    After running unicrawl/spiders/{school}_coursess.py, courses can be split over several lines
     (due to the way the website is organised). The goal of this function is to merge those lines
     to have one line per course
    """

    # Read the programs file
    courses_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}_pre.json")
    courses_df = pd.read_json(courses_fn)

    # Group different keys
    if school != 'ugent':
        courses_df = courses_df.set_index("id")
        courses_df_grouped = courses_df.groupby("id")
        courses_merged_df = courses_df_grouped["name"].unique().apply(lambda x: x[0]).to_frame()
    else:
        courses_df_grouped = courses_df.groupby("name")
        courses_merged_df = courses_df_grouped["id"].unique().apply(lambda x: x[0]).to_frame()
    for key in ["year", "url"]:
        courses_merged_df[key] = courses_df_grouped[key].apply(lambda x: x.iloc[0])
    for key in ["content", "goal", "activity", "other"]:
        courses_merged_df[key] = courses_df_grouped[key].apply(lambda x: "\n".join(x.values))
    courses_merged_df['languages'] = courses_df_grouped["languages"].sum().apply(lambda x: list(set(x)))
    courses_merged_df['teachers'] = courses_df_grouped["teachers"].sum().apply(lambda x: list(set(x)))

    courses_merged_df = courses_merged_df.reset_index().set_index("id")

    courses_merged_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json")
    courses_merged_df.reset_index().to_json(courses_merged_fn, orient='records')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", help='course or program', default='course')
    parser.add_argument("-s", "--school", help="input json file path")
    parser.add_argument("-y", "--year", help="academic year", default=2022)
    arguments = vars(parser.parse_args())
    if arguments['type'] == 'course':
        merge_courses(arguments['school'], arguments['year'])
    else:
        merge_programs(arguments['school'], arguments['year'])
