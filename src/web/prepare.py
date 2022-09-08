from pathlib import Path
import argparse

import pandas as pd
import itertools

from settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER, WEB_INPUT_FOLDER

import logging
logger = logging.getLogger()


def add_missing_fields_in_programs(programs_df: pd.DataFrame, courses_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add missing fields to programs info DataFrame.

    For some institutions, information such as faculties, campuses or ects are crawled more
    efficiently by courses than by programs.
    This function serves to add this information back from the courses info DataFrame to the programs info Dataframe

    Parameters
    ----------
    programs_df: pd.DataFrame
        Dataframe containing information about programs of an institution.
        Should contain a column courses containing list of courses identifiers.
        Each course identifier contained in courses_df should be contained in at least one of those least.
    courses_df: pd.DataFrame
        Dataframe containing information about courses of that same institution.
        The index of this dataframe are the courses identifiers.

    """
    # Check if the courses dataframe contains information that should be in the programs dataframe
    keys_normally_in_programs = ["faculties", "campuses", "languages", "ects"]
    keys_in_courses = list(set(courses_df.keys()).intersection(set(keys_normally_in_programs)))
    if len(keys_in_courses) == 0:
        return programs_df

    # Create column for each key to transfer from courses to programs
    for key in keys_in_courses:
        if key not in programs_df.keys():
            programs_df[key] = pd.Series([[]]*len(programs_df), index=programs_df.index)

    # Fill columns
    for idx, courses in programs_df['courses'].items():
        for key in keys_in_courses:
            if len(courses) == 0:
                programs_df[key].loc[idx] = []
                continue
            programs_df[key].loc[idx] = list(set(courses_df.loc[courses, key].sum()))

    return programs_df


def add_fields_to_courses(courses_df: pd.DataFrame, programs_df: pd.DataFrame) -> pd.DataFrame:

    # Add every cycle and field in which each course is given

    # Create new columns
    courses_df["cycles"] = pd.Series([[]]*len(courses_df), index=courses_df.index)
    courses_df["fields"] = pd.Series([[]]*len(courses_df), index=courses_df.index)

    # Loop on programs
    for program_id in programs_df.index:
        cycle = programs_df.loc[program_id, "cycle"]
        fields = programs_df.loc[program_id, "fields"]
        courses = programs_df.loc[program_id, "courses"]
        courses_df.loc[courses, "cycles"] = courses_df.loc[courses, "cycles"].apply(lambda x: x + [cycle])
        courses_df.loc[courses, "fields"] = courses_df.loc[courses, "fields"].apply(lambda x: x + fields)

    # Remove duplicates
    courses_df["cycles"] = courses_df["cycles"].apply(lambda x: list(set(x)))
    courses_df["fields"] = courses_df["fields"].apply(lambda x: list(set(x)))

    return courses_df


def convert_faculty_to_fields(programs_df, school: str):

    fields_fn = Path(__file__).parent.absolute().joinpath("../../data/faculties_to_fields.csv")
    faculties_to_fields_df = pd.read_csv(fields_fn)
    faculties_to_fields_df = faculties_to_fields_df[faculties_to_fields_df.school == school]
    faculties_to_fields_ds = faculties_to_fields_df[["faculty", "fields"]].set_index("faculty")

    def faculty_to_field(faculties):
        for faculty in faculties:
            assert faculty in faculties_to_fields_ds.index, f'Error: {faculty} was not found in faculty_to_fields'
        return list(itertools.chain.from_iterable([faculties_to_fields_ds.loc[faculty][0].split(";")
                                                   for faculty in faculties]))

    programs_df["fields"] = programs_df["faculties"].apply(lambda x: faculty_to_field(x))
    return programs_df


def main(school: str, year: int):

    # Load course crawling output
    courses_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json")
    courses_df = pd.read_json(open(courses_fn, 'r'), dtype={'id': str}).set_index("id")
    courses_df = courses_df.drop(["content", "goal", "activity", "other"], axis=1)

    # Load program crawling output
    programs_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_programs_{year}.json")
    programs_df = pd.read_json(open(programs_fn, 'r'))

    # By default, some keys like "ects", "faculties" and "campuses" should be associated to programs
    # But in some cases, they are associated to courses.
    programs_df = add_missing_fields_in_programs(programs_df, courses_df)

    # Convert faculties to disciplines
    programs_df = convert_faculty_to_fields(programs_df, school)

    # Add fields to course df
    courses_df = add_fields_to_courses(courses_df, programs_df)

    # Load scoring output
    scores_fn = Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}"
                                                          f"{school}_courses_scoring_{year}.csv")
    scores_df = pd.read_csv(scores_fn, dtype={'id': str}).set_index('id')
    courses_with_matches_index = scores_df[(scores_df.sum(axis=1) != 0)].index

    # Generating course file (only courses with score > 0)
    # Convert columns of scores to list of themes
    courses_df["themes"] = scores_df.apply(lambda x: list(set(x[x == 1].index.tolist()) - {"dedicated"}),
                                           axis=1).to_frame()
    courses_df["dedicated"] = scores_df.apply(lambda x: x["dedicated"], axis=1).to_frame()
    courses_df = courses_df.reset_index()
    web_fn = Path(__file__).parent.absolute().joinpath(f"../../{WEB_INPUT_FOLDER}{school}_data_{year}_")
    # courses_df.to_json(f"{web_fn}heavy.json", orient='records')
    courses_df.loc[courses_df.id.isin(courses_with_matches_index)]\
        .to_json(f"{web_fn}courses.json", orient='records', indent=1)

    # Creating program file (only programs with score > 0)
    program_scores_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_programs_scoring_{year}.csv")
    programs_scores_df = pd.read_csv(program_scores_fn, index_col=0)

    # Get for each program the list of courses that matched in at least one theme
    matched_courses = list(courses_df[courses_df.id.isin(courses_with_matches_index)].id)
    programs_df['matched_courses'] = pd.Series([[]]*len(programs_df), index=programs_df.index)
    for program_id, program_courses in programs_df['courses'].items():
        programs_df["matched_courses"].loc[program_id] = list(set(program_courses).intersection(set(matched_courses)))

    # Get programs that matched at least one theme
    programs_with_matches_index = programs_scores_df[(programs_scores_df.sum(axis=1) != 0)].index
    # Get list of matched themes per program and associated scores
    programs_df = programs_df.set_index("id")

    def get_matched_themes(x):
        x = x.drop(["dedicated", "total"])
        return x[x > 0].index.tolist()
    programs_df["themes"] = programs_scores_df.apply(lambda x: get_matched_themes(x), axis=1).to_frame()

    def get_matched_themes_scores(x):
        x = x.drop(["dedicated", "total"])
        return x[x > 0].values.tolist()
    programs_df["themes_scores"] = programs_scores_df.apply(lambda x: get_matched_themes_scores(x), axis=1).to_frame()
    programs_df["nb_dedicated_courses"] = programs_scores_df["dedicated"]
    programs_df = programs_df.reset_index()

    programs_df = programs_df[['id', 'name', 'cycle', 'url',
                               'languages', 'campuses', 'faculties', 'fields',
                               'themes', 'themes_scores', 'matched_courses', 'nb_dedicated_courses'
                               ]]

    programs_df.loc[programs_df.id.isin(programs_with_matches_index)] \
        .to_json(f"{web_fn}programs.json", orient='records', indent=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="input json file path")
    parser.add_argument("-y", "--year", help="academic year", default=2022)
    arguments = vars(parser.parse_args())
    # main(**arguments)

    schools = ["kuleuven", "uantwerpen", "uclouvain", "ugent", "uhasselt",
               "ulb", "uliege", "umons", "unamur", "uslb", "vub"]
    schools += ["artevelde", "ecam", "ecsedi-isalt", "ehb", "he-ferrer", "heaj", "hech", "hel", "heldb", "helmo",
                "henallux", "hepl", "hers", "hogent", "howest", "ichec", "ihecs", "ispg", "issig", "odisee",
                "thomasmore", "ucll", "vinci", "vives"]
    for school in schools:
        print(school)
        main(school, arguments['year'])
