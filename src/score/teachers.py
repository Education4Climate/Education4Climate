""" Aggregate scores by programs """

from pathlib import Path
import argparse

import pandas as pd

from config.settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER, WEB_INPUT_FOLDER


def main(school: str, year: int):

    # Load scoring output for courses
    courses_scores_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}.csv")
    courses_scores_df = pd.read_csv(courses_scores_fn, dtype={'id': str})
    courses_scores_df = courses_scores_df.set_index('id')
    # themes = courses_scores_df.columns
    # Get course with non-zero score
    print(len(courses_scores_df))
    matched_courses_index = courses_scores_df[courses_scores_df.sum(axis=1) > 0].index
    print(len(matched_courses_index))

    # Load teachers
    courses_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json")
    courses_df = pd.read_json(open(courses_fn, 'r'), dtype={'id': str}).set_index("id")[["teacher", "name"]]
    courses_df = courses_df.loc[matched_courses_index]

    # Create table associating teachers to the list of (ids and names of) matched courses they give
    teachers_courses_df = pd.DataFrame(index=set(courses_df['teacher'].sum()), columns=['ids', 'names'], dtype=str)
    for teacher in teachers_courses_df.index:
        courses_b = courses_df['teacher'].apply(lambda teacher_list: teacher in teacher_list)
        teachers_courses_df.loc[teacher, 'ids'] = list(courses_df[courses_b].index)
        teachers_courses_df.loc[teacher, 'names'] = list(courses_df[courses_b]['name'])
    teachers_courses_df = teachers_courses_df.reset_index()
    teachers_courses_df.columns = ['teacher', 'courses_ids', 'courses_names']

    # Save for web app
    teachers_web_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{WEB_INPUT_FOLDER}{school}_data_{year}_teachers.json")
    teachers_courses_df.to_json(teachers_web_fn, orient='records', indent=1)

    # TODO: temporary
    # Save for mailing
    # Divide name and surname
    teachers_courses_df["name"] = teachers_courses_df["teacher"].apply(lambda teacher: teacher.split(" ")[-1])
    teachers_courses_df["surname"] = \
        teachers_courses_df["teacher"].apply(lambda teacher: " ".join(teacher.split(" ")[:-1]))
    teachers_courses_df = teachers_courses_df.drop('teacher', axis=1)
    teachers_mail_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_teachers_{year}.csv")
    print(teachers_courses_df["courses_names"])
    teachers_courses_df[['surname', 'name', 'courses_names']].to_csv(teachers_mail_fn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="input json file path")
    parser.add_argument("-y", "--year", help="academic year", default=2020)
    arguments = vars(parser.parse_args())
    main(**arguments)
