import argparse

import pandas as pd

from config.settings import SCORING_OUTPUT_FOLDER, CRAWLING_OUTPUT_FOLDER, WEB_INPUT_FOLDER

# TODO: for me this should not be in the directory scoring -> nothing to do with it


def main(school: str, year: int):

    # Load courses data
    courses_fn = f"{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json"
    courses_df = pd.read_json(open(courses_fn, 'r'))
    # TODO: shoudln't need this anymore
    # courses_df = courses_df.rename(
    #     columns={"anacs": "year", "class": "name", "teachers": "teacher", "shortname": "id", "location": "campus"})

    # Load courses scoring
    scoring_fn = f"{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}.csv"
    scores = pd.read_csv(scoring_fn)

    # Join course data and scoring
    # TODO: output to json
    # TODO: ask Quentin what he needs as output
    join = courses_df.set_index("id").join(scores.set_index("id"), on="id", how="right")
    output_fn = f"{WEB_INPUT_FOLDER}{school}_data_{year}"
    join.to_csv(output_fn + '_heavy.csv')
    # Also save a light version where we only keep courses with a shift score different from 0
    join[join["shift_score"] != 0].to_csv(output_fn + '_light.csv')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="Input json file path")
    parser.add_argument("-y", "--year", help="Academic year", default=2020)
    arguments = vars(parser.parse_args())
    main(**arguments)
