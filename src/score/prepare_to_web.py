from pathlib import Path
import argparse

import pandas as pd

from config.settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER, WEB_INPUT_FOLDER

import logging
logger = logging.getLogger()


def exchange_fields(courses_df, programs_df):

    # By default, courses should contain the following keys at minima (+ id)
    keys_in_courses = ["name", "year", "teachers", "languages", "url"]
    # If convenient, courses can also contain the following information. If they don't, we are adding them back in.
    # TODO: why is cycle not here?
    keys_in_programs = ["ects", "faculty", "campus"]
    keys_not_in_courses = ["ects", "faculty", "campus"]
    # First, we identify in which dataframes those 'programs keys' are and update the lists accordingly
    for key in keys_in_programs:
        if key in courses_df.columns:
            keys_in_courses.append(key)
            keys_not_in_courses.remove(key)
    # Keep only those columns (drop for example the column 'content')
    courses_df = courses_df[keys_in_courses]
    # TODO: actually change that in the crawler
    # If 'program keys' were directly in courses, they might not be in list format
    for key in keys_in_programs:
        if key in keys_in_courses:
            courses_df[key] = courses_df[key].apply(lambda x: [x] if not isinstance(x, list) else x)
            courses_df[key] = courses_df[key].apply(lambda x: list(set(x)))

    # Finally, we add to the courses dataframe, the 'program data' that was not already in there
    # TODO: maybe a more efficient way to do this
    courses_aux_df = pd.DataFrame(index=courses_df.index, columns=keys_not_in_courses)
    for course_id in courses_aux_df.index:
        ects = []
        faculty = []
        campus = []
        # Check all programs to see if the course is in there and fetch info
        for program_id in programs_df.index:
            program_courses = programs_df.loc[program_id, 'courses']
            if course_id in program_courses:
                if 'ects' in keys_in_programs:
                    # Ects should be in a list at the same position as the course in the courses list
                    ects += [programs_df.loc[program_id, 'ects'][program_courses.index(course_id)]]
                if 'faculty' in keys_in_programs:
                    faculty += [programs_df.loc[program_id, 'faculty']]
                if 'campus' in keys_in_programs:
                    campus += [programs_df.loc[program_id, 'campus']]
        # Add the lists to the dataframe if required
        if 'ects' in keys_in_programs:
            courses_aux_df.loc[course_id, 'ects'] = list(set(ects))
        if 'faculty' in keys_in_programs:
            courses_aux_df.loc[course_id, 'faculty'] = list(set(faculty))
        if 'campus' in keys_in_programs:
            courses_aux_df.loc[course_id, 'campus'] = list(set(campus))

    courses_df = pd.concat([courses_df, courses_aux_df], axis=1)

    return courses_df


def convert_faculty_to_thematics(courses_df, programs_df, school: str):
    fields_fn = Path(__file__).parent.absolute().joinpath("../../data/faculties_to_fields.csv")
    faculties_to_fields_df = pd.read_csv(fields_fn)
    faculties_to_fields_df = faculties_to_fields_df[faculties_to_fields_df.school == school]
    faculties_to_fields_ds = faculties_to_fields_df[["faculty", "field"]].set_index("faculty")

    def faculty_to_field(faculty):
        if faculty in faculties_to_fields_ds.index:
            return faculties_to_fields_ds.loc[faculty][0]
        else:
            logger.warning(f"Warning: {faculty} was not found in faculty_to_fields")
            return ''

    courses_df["field"] = courses_df["faculty"].apply(lambda x: list(set([faculty_to_field(i) for i in x])))
    programs_df["field"] = programs_df["faculty"].apply(lambda x: faculty_to_field(x))
    return courses_df, programs_df


def main(school: str, year: int):

    # Load course crawling output
    courses_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json")
    courses_df = pd.read_json(open(courses_fn, 'r'), dtype={'id': str}).set_index("id")
    courses_df = courses_df.drop("content", axis=1)

    # Load program crawling output
    programs_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_programs_{year}.json")
    programs_df = pd.read_json(open(programs_fn, 'r'))

    # By default, some keys like "ects", "faculty" and "campus" should be associated to programs
    # But in some cases, they are associated to courses.
    courses_df = exchange_fields(courses_df, programs_df)

    # Convert faculties to disciplines
    courses_df, programs_df = convert_faculty_to_thematics(courses_df, programs_df, school)

    # Load scoring output
    scores_fn = Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}.csv")
    scores_df = pd.read_csv(scores_fn, dtype={'id': str}).set_index('id')
    courses_with_matches_index = scores_df[(scores_df.sum(axis=1) != 0)].index

    # Generating heavy version and light version (only courses with score > 0)
    # Convert columns of scores to list of themes
    courses_df["themes"] = scores_df.apply(lambda x: x[x == 1].index.tolist(), axis=1).to_frame()
    courses_df = courses_df.reset_index()
    web_fn = Path(__file__).parent.absolute().joinpath(f"../../{WEB_INPUT_FOLDER}{school}_data_{year}_")
    courses_df.to_json(f"{web_fn}heavy.json", orient='records')
    courses_df.loc[courses_df.id.isin(courses_with_matches_index)]\
        .to_json(f"{web_fn}light.json", orient='records', indent=1)

    # Creating program file (only programs with score > 0)
    program_scores_fn = \
        Path(__file__).parent.absolute().joinpath(f"../../{SCORING_OUTPUT_FOLDER}{school}_programs_scoring_{year}.csv")
    programs_scores_df = pd.read_csv(program_scores_fn, index_col=0)

    # Get for each program the list of courses that matched in at least one them
    matched_courses = list(courses_df[courses_df.id.isin(courses_with_matches_index)].id)
    for program_id, program_courses in programs_df['courses'].items():
        programs_df.loc[program_id]['courses'] = list(set(program_courses).intersection(set(matched_courses)))

    # Get programs that matched at least one theme
    programs_with_matches_index = programs_scores_df[(programs_scores_df.sum(axis=1) != 0)].index
    # Get list of matched themes per program and associated scores
    programs_df = programs_df.set_index("id")
    programs_df["themes"] = programs_scores_df.apply(lambda x: x[x > 0].index.tolist(), axis=1).to_frame()
    programs_df["themes_scores"] = programs_scores_df.apply(lambda x: x[x > 0].values.tolist(), axis=1).to_frame()
    programs_df = programs_df.reset_index()

    # TODO: keep or remove ects?
    programs_df = programs_df[['id', 'name', 'faculty', 'cycle', 'campus', 'url', 'courses',
                               'field', 'themes', 'themes_scores']]

    programs_df.loc[programs_df.id.isin(programs_with_matches_index)] \
        .to_json(f"{web_fn}programs.json", orient='records', indent=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="input json file path")
    parser.add_argument("-y", "--year", help="academic year", default=2020)
    arguments = vars(parser.parse_args())
    main(**arguments)
