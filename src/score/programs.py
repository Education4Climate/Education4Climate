""" Aggregate scores by programs """

from pathlib import Path
import argparse

import pandas as pd

from settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER


def main(school: str, year: int):

    # Load programs crawling output
    programs_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_programs_{year}.json")
    programs_courses_ds = pd.read_json(open(programs_fn, 'r'), dtype={'id': str}).set_index("id")["courses"].squeeze()

    # Load scoring output for courses
    courses_scores_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_courses_scoring_{year}.csv")
    courses_scores_df = pd.read_csv(courses_scores_fn, dtype={'id': str})
    courses_scores_df = courses_scores_df.set_index('id')
    themes = courses_scores_df.columns

    # Sum courses scores into programs scores
    programs_scores_df = pd.DataFrame(index=programs_courses_ds.index, columns=themes, dtype=int)
    for program_id, program_courses in programs_courses_ds.items():
        # Remove non-scored courses from list (could happen if the course was not crawlable)
        program_courses = list(set(program_courses).intersection(set(courses_scores_df.index)))
        programs_scores_df.loc[program_id] = courses_scores_df.loc[program_courses].sum()
        programs_scores_df.loc[program_id, 'total'] = int(courses_scores_df.loc[program_courses].max(axis=1).sum())

    programs_scores_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_programs_scoring_{year}.csv")
    programs_scores_df.astype(int).to_csv(programs_scores_fn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="input json file path")
    parser.add_argument("-y", "--year", help="academic year", default=2020)
    arguments = vars(parser.parse_args())
    main(**arguments)
