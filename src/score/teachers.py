""" Aggregate scores by programs """

from pathlib import Path
import argparse
from typing import List

import pandas as pd

from settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER


def get_teachers_info(school: str, year: int):

    # Load scoring output for courses
    courses_scores_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_courses_scoring_{year}.csv")
    courses_scores_df = pd.read_csv(courses_scores_fn, dtype={'id': str})
    courses_scores_df = courses_scores_df.set_index('id')
    # themes = courses_scores_df.columns
    # Get course with non-zero score
    matched_courses_index = courses_scores_df[courses_scores_df.sum(axis=1) > 0].index

    # Load teachers
    courses_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json")
    courses_df = pd.read_json(open(courses_fn, 'r'), dtype={'id': str}).set_index("id")[["teachers", "name"]]
    courses_df = courses_df.loc[matched_courses_index]

    # Create table associating teachers to the list of (ids and names of) matched courses they give
    teachers_courses_df = pd.DataFrame(index=set(courses_df['teachers'].sum()), columns=['ids', 'names'], dtype=str)
    for teacher in teachers_courses_df.index:
        courses_b = courses_df['teachers'].apply(lambda teacher_list: teacher in teacher_list)
        teachers_courses_df.loc[teacher, 'ids'] = list(courses_df[courses_b].index)
        teachers_courses_df.loc[teacher, 'names'] = list(courses_df[courses_b]['name'])
    teachers_courses_df = teachers_courses_df.reset_index()
    teachers_courses_df.columns = ['teacher', 'courses_ids', 'courses_names']
    teachers_courses_df['courses_number'] = teachers_courses_df["courses_names"].apply(lambda x: len(x))

    # Divide name and surname (some schools start with the surname, other with the name
    teachers_courses_df["name"] = teachers_courses_df["teacher"].apply(lambda teacher: teacher.split(" ")[-1])
    teachers_courses_df["surname"] = \
        teachers_courses_df["teacher"].apply(lambda teacher: " ".join(teacher.split(" ")[:-1]))
    teachers_courses_df = teachers_courses_df.drop('teacher', axis=1)

    return teachers_courses_df[['surname', 'name', 'courses_names', 'courses_number']]

    # Save for mailing
    # teachers_mail_fn = \
    #     Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_teachers_{year}.csv")
    # teachers_courses_df[['surname', 'name', 'courses_names', 'courses_number']].to_csv(teachers_mail_fn)


def main(schools: List[str], year: int):

    fn = Path(__file__).parent.absolute().joinpath(f"../../data/teachers_{year}.xlsx")
    with pd.ExcelWriter(fn) as writer:
        for school in schools:
            print(school)
            teachers_courses_df = get_teachers_info(school, year)
            teachers_courses_df.to_excel(writer, sheet_name=school, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("-s", "--school", help="input json file path")
    parser.add_argument("-y", "--year", help="academic year", default=2020)
    arguments = vars(parser.parse_args())
    schools_ = ["kuleuven", "uantwerpen", "uclouvain", "ugent", "uhasselt",
                "ulb", "uliege", "umons", "unamur", "uslb", "vub"]
    schools_ = ["artevelde", "ecam", "ecsedi-isalt", "ehb", "he-ferrer", "hech", "hel", "heldb", "helmo",
                "henallux", "hers", "howest", "ichec", "ihecs", "ispg", "issig", "odisee", "thomasmore", "ucll",
                "vinci", "vives"]
    arguments['schools'] = schools_
    main(**arguments)
