""" Aggregate scores by programs """

import argparse

import pandas as pd

from config.settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER


def main(school: str, year: int):

    # Load programs crawling output
    programs_fn = f"../../{CRAWLING_OUTPUT_FOLDER}{school}_programs_{year}.json"
    programs_courses_ds = pd.read_json(open(programs_fn, 'r')).set_index("id")["courses"].squeeze()

    # Load scoring output for courses
    courses_scores_fn = f"../../{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}.csv"
    courses_scores_df = pd.read_csv(courses_scores_fn, index_col=0)
    themes = courses_scores_df.columns

    # Sum courses scores into programs scores
    programs_scores_df = pd.DataFrame(index=programs_courses_ds.index, columns=themes, dtype=int)
    for program_id, program_courses in programs_courses_ds.items():
        programs_scores_df.loc[program_id] = courses_scores_df.loc[program_courses].sum()

    programs_scores_fn = f"../../{SCORING_OUTPUT_FOLDER}{school}_programs_scoring_{year}.csv"
    programs_scores_df.astype(int).to_csv(programs_scores_fn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="input json file path")
    parser.add_argument("-y", "--year", help="academic year", default=2020)
    arguments = vars(parser.parse_args())
    main(**arguments)