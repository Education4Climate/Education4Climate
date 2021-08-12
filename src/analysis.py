from typing import List
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from settings import SCORING_OUTPUT_FOLDER, CRAWLING_OUTPUT_FOLDER

import logging
logger = logging.getLogger()


def get_fields():
    fields_fn = Path(__file__).parent.absolute().joinpath("../data/faculties_to_fields.csv")
    return pd.read_csv(fields_fn)['field'].unique()


def convert_faculty_to_fields(programs_df, school: str):
    fields_fn = Path(__file__).parent.absolute().joinpath("../data/faculties_to_fields.csv")
    faculties_to_fields_df = pd.read_csv(fields_fn)
    faculties_to_fields_df = faculties_to_fields_df[faculties_to_fields_df.school == school]
    faculties_to_fields_ds = faculties_to_fields_df[["faculty", "field"]].set_index("faculty")

    def faculty_to_field(faculty):
        if faculty in faculties_to_fields_ds.index:
            return faculties_to_fields_ds.loc[faculty][0]
        else:
            logger.warning(f"Warning: {faculty} was not found in faculty_to_fields")
            return 'other'

    programs_df["field"] = programs_df["faculty"].apply(lambda x: faculty_to_field(x))
    return programs_df


def analyse_courses(schools: List[str], year: int, themes: List[str]):

    number_of_courses_per_school = pd.Series(index=schools, dtype=float)
    number_of_matched_courses_per_theme = pd.DataFrame(index=schools, columns=themes, dtype=int)
    number_of_matched_courses_in_any_theme = pd.Series(0., index=schools, dtype=int)

    for school in schools:
        # Read score for school
        course_scores_fn = Path(__file__).parent.absolute()\
            .joinpath(f"../{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}.csv")
        courses_scores = pd.read_csv(course_scores_fn, index_col=0)
        print(school, len(courses_scores))
        number_of_courses_per_school[school] = len(courses_scores)
        number_of_matched_courses_per_theme.loc[school] = courses_scores.sum(axis=0)
        number_of_matched_courses_in_any_theme[school] += courses_scores.max(axis=1).sum()

    print(f"\nNumber of courses per school\n{number_of_courses_per_school}")
    number_of_courses_per_school.apply(lambda x: x/1000.).sort_values().plot(kind='bar', figsize=(12, 12),
                                                                             title='Number of courses (in thousands)')
    print(f"\nNumber of matched courses per theme\n{number_of_matched_courses_per_theme.astype(int)}")
    perc_of_matched_course_per_theme = number_of_matched_courses_per_theme.div(number_of_courses_per_school, axis=0)*100
    #perc_of_matched_course_per_theme.plot(kind='bar', figsize=(12, 12), ylabel='%',
    #                                      title='Percentage of matched courses per theme')
    print(f"\nPercentage of matched courses per theme\n{perc_of_matched_course_per_theme.round(2)}")
    print(f"\nNumber of matched courses in any theme\n{number_of_matched_courses_in_any_theme}")
    perc_of_matched_course_in_any_theme = number_of_matched_courses_in_any_theme*100/number_of_courses_per_school
    # plt.figure()
    #perc_of_matched_course_in_any_theme.plot(kind='bar', figsize=(12, 12), ylabel='%',
    #                                         title='Percentage of matched courses in any theme')
    print(f"\nPercentage of matched courses in any theme\n{perc_of_matched_course_in_any_theme.round(2)}")
    #plt.show()


def analyse_programs(schools: List[str], year: int, themes: List[str], matched: bool = True):

    number_of_programs_per_school = pd.Series(index=schools, dtype=int)
    number_of_programs_per_field = pd.Series(0, index=get_fields(), dtype=int)
    number_of_programs_per_cycle = pd.Series(0, index=['bac', 'master', 'other', 'certificate', 'minor',
                                                       'doctor', 'postgrad'], dtype=int)
    number_of_matched_programs_per_theme = pd.Series(index=themes, dtype=int)
    number_of_matched_programs_in_any_theme = 0.
    # avg_perc_of_matched_courses_per_program_per_theme = pd.Series(index=themes, dtype=int)

    # Get data for all schools
    for school in schools:
        print(school)
        programs_data_fn = Path(__file__).parent.absolute()\
            .joinpath(f"../{CRAWLING_OUTPUT_FOLDER}{school}_programs_{year}.json")
        programs_df = pd.read_json(programs_data_fn, orient='records').set_index("id")

        # Keep only programs that have matched courses if desired
        programs_scores_fn = Path(__file__).parent.absolute()\
            .joinpath(f"../{SCORING_OUTPUT_FOLDER}{school}_programs_scoring_{year}.csv")
        programs_scores = pd.read_csv(programs_scores_fn, index_col=0)

        if matched:
            matched_programs_ids = programs_scores[programs_scores.apply(lambda x: x.sum() > 0, axis=1)].index
            programs_df = programs_df.loc[matched_programs_ids]

        programs_df = convert_faculty_to_fields(programs_df, school)
        number_of_programs_per_field[programs_df["field"].unique()]\
            += programs_df.groupby("field")["name"].count()
        number_of_programs_per_cycle[programs_df["cycle"].unique()]\
            += programs_df.groupby("cycle")["name"].count()
        # number_of_programs_per_school[school] = len(programs_scores)
        # number_of_matched_programs_per_theme += programs_scores.apply(lambda x: x > 0).sum(axis=0)
        # number_of_matched_programs_in_any_theme += programs_scores.apply(lambda x: x > 0).max(axis=1).sum()

        # Get number of courses per program (that have at least one matched course)
        # programs_info_fn = Path(__file__).parent.absolute()\
        #     .joinpath(f"../{CRAWLING_OUTPUT_FOLDER}{school}_programs_{year}.json")
        # programs_info = pd.read_json(programs_info_fn).set_index("id")
        # number_of_courses_per_program = programs_info['courses'].apply(lambda x: len(x))
        # for theme in themes:
        #     matched_programs = programs_scores[programs_scores[theme] > 0].index
        #     matched_programs_scores = programs_scores.loc[matched_programs, theme]
        #     matched_programs_number_of_courses = number_of_courses_per_program[matched_programs]
        #      avg_perc_of_matched_courses_per_program_per_theme.loc[theme] = \
        #         (matched_programs_scores.div(matched_programs_number_of_courses, axis=0)).median(axis=0)
    plt.figure()
    number_of_programs_per_field.plot(kind='pie', title='', label='')
    plt.figure()
    number_of_programs_per_cycle.plot(kind='bar')
    return
    exit()

    print(f"\nNumber of programs per school\n{number_of_programs_per_school}")
    # number_of_programs_per_school.apply(lambda x: x/100.).sort_values().plot(kind='bar', figsize=(12, 12),
    #                                                                          title='Number of programs (in hundreds)')

    print(f"\nNumber of matched programs per theme\n{number_of_matched_programs_per_theme.astype(int)}")
    perc_of_matched_programs_per_theme = \
        number_of_matched_programs_per_theme*100/number_of_programs_per_school.sum()
    print(f"\nPercentage of matched programs per theme\n{perc_of_matched_programs_per_theme.round(2)}")
    # perc_of_matched_programs_per_theme.plot(kind='bar', figsize=(12, 12), ylabel='%',
    #                                        title='Percentage of matched programs per theme')
    print(f"\nNumber of matched programs in any theme: {number_of_matched_programs_in_any_theme:.0f}")
    perc_of_matched_programs_in_any_theme = number_of_matched_programs_in_any_theme*100/number_of_programs_per_school.sum()
    print(f"\nPercentage of matched programs in any theme: {perc_of_matched_programs_in_any_theme:.2f}")
    # plt.figure()
    # perc_of_matched_programs_in_any_theme.plot(kind='bar', figsize=(12, 12), ylabel='%',
    #                                           title='Percentage of matched courses in any theme')
    # print(f"\nMedian percentage of matched courses per program (that had at least one matched course)"
    #      f"\n{avg_perc_of_matched_courses_per_program_per_theme.round(4)*100}")
    #plt.show()


if __name__ == '__main__':
    schools_ = ["ucl", "uliege", "ulb", "umons", "unamur", "uslb", "kuleuven", "vub", "uantwerpen", "ugent", "uhasselt"]
    themes_ = ["climatology", "decarbonization", "durability", "energy", "environment", "society"]
    # analyse_courses(schools_, 2020, themes_)
    analyse_programs(schools_, 2020, themes_, False)
    analyse_programs(schools_, 2020, themes_)
    plt.show()
