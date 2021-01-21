import argparse

import pandas as pd

from config.settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER, WEB_INPUT_FOLDER


def main(school: str, year: int):

    # Load crawling output
    courses_fn = f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json"
    courses_df = pd.read_json(open(courses_fn, 'r')).set_index("id")
    courses_df = courses_df.drop("content", axis=1)

    # Load scoring output
    scores_fn = f"../../{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}.csv"
    scores_df = pd.read_csv(scores_fn, index_col=0)

    # Generating heavy version and light version (only courses with score > 0)
    web_df = courses_df.join(scores_df, on="id", how="right").reset_index()
    web_fn = f"../../{WEB_INPUT_FOLDER}{school}_data_{year}_"
    web_df.to_json(web_fn + "heavy.json", orient='records')
    web_df[web_df["shift_score"] != 0].to_json(web_fn + 'light.json', orient='records', indent=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="input json file path")
    parser.add_argument("-y", "--year", help="academic year", default=2020)
    arguments = vars(parser.parse_args())
    main(**arguments)
