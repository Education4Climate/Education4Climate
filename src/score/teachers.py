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
    courses_teachers_ds = pd.read_json(open(courses_fn, 'r'), dtype={'id': str}).set_index("id")["teacher"].squeeze()
    courses_teachers_ds = courses_teachers_ds[matched_courses_index]

    print(courses_teachers_ds.apply(lambda x: len(x)).median())
    print(courses_teachers_ds.apply(lambda x: len(x)).sum())
    # for idx in courses_teachers_ds.index:
    #     print(len(courses_teachers_ds[idx]))
    print(len(set(courses_teachers_ds.sum())))
    print(set(courses_teachers_ds.sum()))
    # Find teachers that are associated to courses with non-zero scores
    teachers_courses_ds = pd.Series(index=set(courses_teachers_ds.sum()), dtype=str)
    for teacher in teachers_courses_ds.index:
        courses = list(courses_teachers_ds[courses_teachers_ds
                       .apply(lambda teacher_list: teacher in teacher_list)].index)
        teachers_courses_ds[teacher] = courses
    teachers_courses_df = teachers_courses_ds.to_frame().reset_index()
    teachers_courses_df.columns = ['teacher', 'courses']

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
    teachers_courses_df[['surname', 'name', 'courses']].to_csv(teachers_mail_fn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="input json file path")
    parser.add_argument("-y", "--year", help="academic year", default=2020)
    arguments = vars(parser.parse_args())
    main(**arguments)
