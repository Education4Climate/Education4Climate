import pandas as pd
import json
import os

from ast import literal_eval
from pathlib import Path

from settings import (CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER, SCORING_ANALYSIS_FOLDER, YEAR, ACCEPTED_LANGUAGES,
                      WEB_INPUT_FOLDER)


def get_matched_patterns_per_course(schools, year, scoring_folder=SCORING_OUTPUT_FOLDER,
                                    scoring_analysis_folder=SCORING_ANALYSIS_FOLDER):
    """
    TODO:
     - Output an excel file with one page per school, and for each course the list of patterns
       that matched in each language
    """

    fn = Path(os.path.abspath('')).parent.absolute().joinpath(
                f"../{scoring_analysis_folder}matched_patterns_per_course.xlsx")
    with pd.ExcelWriter(fn) as writer:

        for school in schools:
            print(school)

            # Read matches file
            matches_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
                f"../{scoring_folder}{school}_matches_{year}.json")
            matches_json = json.load(open(matches_fn, 'r'))

            # Read course file to get course name, url, and empty text
            courses_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
                f"../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json")
            courses_df = pd.read_json(courses_fn, orient='records', dtype=str).set_index('id')[['name', 'url',
                                                                                                'content', 'goal']]
            courses_df['content_present'] = courses_df['content'].apply(lambda x: int(len(x) != 0))
            courses_df['goal_present'] = courses_df['goal'].apply(lambda x: int(len(x) != 0))
            courses_df['content_or_goal_present'] = courses_df['content_present'] | courses_df['goal_present']
            empty_patterns_df = pd.DataFrame(index=courses_df.index,
                                             columns=['matched', 'nb_patterns'] + ACCEPTED_LANGUAGES)
            courses_df = pd.concat((courses_df['name'], empty_patterns_df,
                                    courses_df[['url', 'content_present', 'goal_present', 'content_or_goal_present']]),
                                   axis=1)
            courses_df['matched'] = 0
            courses_df['nb_patterns'] = 0

            # For each matched courses in the matched dictionary, get the matched patterns in each language
            for courses_id_name in matches_json.keys():
                course_id = courses_id_name.split(':')[0]
                for lang in matches_json[courses_id_name].keys():
                    patterns = list(matches_json[courses_id_name][lang].keys())
                    courses_df.loc[course_id, lang] = " // ".join(patterns)
                    courses_df.loc[course_id, 'nb_patterns'] += len(patterns)
                    courses_df.loc[course_id, 'matched'] = 1
            # Write output
            courses_df.sort_index().to_excel(writer, sheet_name=school)


def get_number_of_matches_per_pattern(schools, year, dictionary_name, scoring_folder=SCORING_OUTPUT_FOLDER,
                                      scoring_analysis_folder=SCORING_ANALYSIS_FOLDER):
    """
    TODO:
     - output a file with number of matches for each pattern per uni and total
    """

    # Get all matching files
    matches_json_dict = dict.fromkeys(schools)
    for school in schools:
        matches_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
            f"../{scoring_folder}{school}_matches_{year}.json")
        matches_json_dict[school] = json.load(open(matches_fn, 'r'))

    # Get list of patterns
    patterns_dict = {}
    for lang in ACCEPTED_LANGUAGES:
        themes_fn = Path(__file__).parent.absolute().joinpath(f"../../data/patterns/{dictionary_name}/{lang}.csv")
        lang_patterns_df = pd.read_csv(themes_fn, converters={'themes': literal_eval})
        patterns_dict[lang] = lang_patterns_df

    # Count number of times each pattern has matched
    counting_dict = {}
    for lang in ACCEPTED_LANGUAGES:
        # Create counting dataframe
        counting_dict[lang] = pd.DataFrame(0, index=patterns_dict[lang]["patterns"], columns=schools, dtype=int)
        for school in schools:
            # Count the number of matches per pattern
            for v in matches_json_dict[school].values():
                if lang in v:
                    matched_patterns = v[lang].keys()
                    for p in matched_patterns:
                        counting_dict[lang].loc[p, school] += 1

        # Count total across universities
        counting_dict[lang]["total"] = counting_dict[lang].sum(axis=1)

        # Put total column first
        counting_dict[lang] = counting_dict[lang][['total'] + schools]

        # Sort values according to total column
        counting_dict[lang] = counting_dict[lang].sort_values(by='total', ascending=False)

    # Saving dictionary to excel file
    fn = Path(os.path.abspath('')).parent.absolute().joinpath(
            f"../{scoring_analysis_folder}number_matches_per_pattern_{dictionary_name}.xlsx")
    with pd.ExcelWriter(fn) as writer:
        for lang in ACCEPTED_LANGUAGES:
            counting_dict[lang].to_excel(writer, sheet_name=lang)


def get_concurrent_patterns(schools, pattern):
    """
    Output: list of courses that have matched with this pattern and list of patterns that have matched with this course
    """

    dir_name = "/home/duboisa1/shifters/Education4Climate/data/scoring-analysis/"
    input_fn = f"{dir_name}matched_patterns_per_course.xlsx"
    output_fn = f"{dir_name}/matched_patterns_per_course_filtered.xlsx"
    with pd.ExcelWriter(output_fn) as writer:
        for school in schools:
            print(school)
            school_df = pd.read_excel(open(input_fn, 'rb'), sheet_name=school)
            # Remove course that do not have the pattern
            school_df = school_df.dropna(subset=["fr"])
            school_df = school_df[school_df["fr"].apply(lambda x: any([i == pattern for i in x.split(" // ")]))]
            # Rearrange columns
            if len(school_df) != 0:
                school_df = school_df[['id', 'name', 'matched', 'url', 'fr']]
                school_df.to_excel(writer, sheet_name=school)


def get_pattern_matrix_match(schools, year, dictionary_name, scoring_folder=SCORING_OUTPUT_FOLDER):
    """
    Generate an Excel file with one sheet per language containing a matrix, indicating which
    pattern match at the same time and for how many courses
    """

    # Get all matching files
    matches_json_dict = dict.fromkeys(schools)
    for school in schools:
        matches_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
            f"../{SCORING_OUTPUT_FOLDER}{school}_matches_{year}.json")
        matches_json_dict[school] = json.load(open(matches_fn, 'r'))

    # Get list of patterns
    patterns_dict = {}
    for lang in ACCEPTED_LANGUAGES:
        themes_fn = Path(__file__).parent.absolute().joinpath(f"../../data/patterns/{dictionary_name}/{lang}.csv")
        lang_patterns_df = pd.read_csv(themes_fn, converters={'themes': literal_eval})
        patterns_dict[lang] = lang_patterns_df

    # Get list of courses for each schools
    courses_dict = {}
    for school in schools:
        scores_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
            f"../{SCORING_OUTPUT_FOLDER}{school}_courses_scoring_{year}.csv")
        courses_dict[school] = pd.read_csv(scores_fn, dtype={'id': str})['id'].tolist()

    # Count number of times each pattern has matched
    lang_dict = {}
    for lang in ACCEPTED_LANGUAGES:
        # Create counting dataframe
        patterns_patterns_matrix = pd.DataFrame(0, index=patterns_dict[lang]["patterns"],
                                                columns=patterns_dict[lang]["patterns"], dtype=int)
        for school in schools:
            patterns_course_matrix = pd.DataFrame(0, index=patterns_dict[lang]["patterns"],
                                                  columns=courses_dict[school], dtype=int)
            print(school)
            # Count the number of matches per pattern
            for course_id, v in matches_json_dict[school].items():
                course_id = course_id.split(":")[0]
                if lang in v:
                    matched_patterns = v[lang].keys()
                    for p in matched_patterns:
                        patterns_course_matrix.loc[p, course_id] = 1

            # Add the result for this school
            patterns_patterns_matrix += patterns_course_matrix.dot(patterns_course_matrix.T)

        lang_dict[lang] = patterns_patterns_matrix

    # Saving dictionary to excel file
    fn = f"/home/duboisa1/shifters/Education4Climate/data/scoring-analysis/" \
         f"pattern_pattern_matrix_dic_{dictionary_name}.xlsx"
    with pd.ExcelWriter(fn) as writer:
        for lang in ACCEPTED_LANGUAGES:
            lang_dict[lang].to_excel(writer, sheet_name=lang)

# TODO: this is shit, probably to remove
from src.web.prepare import add_missing_fields_in_programs, convert_faculty_to_fields, add_fields_to_courses
def create_programs_excel_file(schools, year):
    """
    Concatenate school data programs into one excel file
    """
    dir_name = "/home/duboisa1/shifters/Education4Climate/data/scoring-analysis/"
    output_fn = f"{dir_name}/programs_results.xlsx"
    with pd.ExcelWriter(output_fn) as writer:
        for school in schools:

            # Load course crawling output
            courses_fn = \
                Path(__file__).parent.absolute().joinpath(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{year}.json")
            courses_df = pd.read_json(open(courses_fn, 'r'), dtype={'id': str}).set_index("id")
            courses_df = courses_df.drop(["content", "goal", "activity", "other"], axis=1)

            # Load program crawling output
            programs_fn = \
                Path(__file__).parent.absolute().joinpath(
                    f"../../{CRAWLING_OUTPUT_FOLDER}{school}_programs_{year}.json")
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
            courses_df["themes"] = scores_df.apply(
                lambda x: sorted(list(set(x[x == 1].index.tolist()) - {"dedicated"})),
                axis=1).to_frame()
            courses_df["dedicated"] = scores_df.apply(lambda x: x["dedicated"], axis=1).to_frame()
            courses_df = courses_df.reset_index()
            web_fn = Path(__file__).parent.absolute().joinpath(f"../../{WEB_INPUT_FOLDER}{school}_data_{year}_")

            # Creating program file (only programs with score > 0)
            program_scores_fn = \
                Path(__file__).parent.absolute().joinpath(
                    f"../../{SCORING_OUTPUT_FOLDER}{school}_programs_scoring_{year}.csv")
            programs_scores_df = pd.read_csv(program_scores_fn, index_col=0)

            # Get for each program the list of courses that matched in at least one theme
            matched_courses = list(courses_df[courses_df.id.isin(courses_with_matches_index)].id)
            programs_df['matched_courses'] = pd.Series([[]] * len(programs_df), index=programs_df.index)
            for program_id, program_courses in programs_df['courses'].items():
                programs_df["matched_courses"].loc[program_id] = sorted(
                    list(set(program_courses).intersection(set(matched_courses))))

            # Count the total and matched number of courses per program
            programs_df["nb_total_courses"] = programs_df.courses.apply(lambda x: len(x))
            programs_df["nb_matched_courses"] = programs_df.matched_courses.apply(lambda x: len(x))

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

            programs_df["themes_scores"] = programs_scores_df.apply(lambda x: get_matched_themes_scores(x),
                                                                    axis=1).to_frame()
            programs_df["nb_dedicated_courses"] = programs_scores_df["dedicated"]
            programs_df = programs_df.reset_index()

            if len(programs_df) != 0:
                programs_df = programs_df[['id', 'name', 'cycle', 'url', 'faculties', 'fields',
                                           'nb_total_courses', 'nb_matched_courses', 'nb_dedicated_courses']]
                programs_df.set_index('id').sort_index().to_excel(writer, sheet_name=school)


if __name__ == "__main__":

    schools_ = ["kuleuven", "uantwerpen", "ugent", "uhasselt", "vub"]
    schools_ += ["artevelde", "ehb", "hogent", "howest", "odisee", "thomasmore", "ucll", "vives"]

    schools_ = ['vives']

    # schools_ = ["uclouvain", "ulb", "uliege", "umons", "unamur", "uslb"]
    # schools_ += ["ecam", "ecsedi-isalt", "he-ferrer", "heaj", "hech", "hel", "heldb", "helmo",
    #              "henallux", "hepl", "hers", "ichec", "ihecs", "ispg", "issig", "vinci"]

    # get_pattern_matrix_match(schools_, 'v2.0')
    # get_number_of_matches_per_pattern(schools_, 'v2.0')
    get_matched_patterns_per_course(schools_, 2022, scoring_folder="/data/scoring-output/")
    create_programs_excel_file(schools_, 2022)
    # get_concurrent_patterns(schools_, "dumping environnement")
