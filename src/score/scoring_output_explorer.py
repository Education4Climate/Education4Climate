import pandas as pd
import json
import os

from ast import literal_eval
from pathlib import Path

from settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER, YEAR, ACCEPTED_LANGUAGES


def get_matched_patterns_per_course(schools, scoring_folder=SCORING_OUTPUT_FOLDER):
    """
    TODO:
     - Output an excel file with one page per school, and for each course the list of patterns
       that matched in each language
    """

    fn = "/home/duboisa1/shifters/Education4Climate/data/scoring-analysis/matched_patterns_per_course.xlsx"
    with pd.ExcelWriter(fn) as writer:

        for school in schools:

            # Read matches file
            matches_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
                f"../{scoring_folder}{school}_matches_{YEAR}.json")
            matches_json = json.load(open(matches_fn, 'r'))

            # Read course file to get course name
            courses_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
                f"../{CRAWLING_OUTPUT_FOLDER}{school}_courses_{YEAR}.json")
            print(courses_fn)
            courses_df = pd.read_json(courses_fn, orient='records', dtype=str).set_index('id')[['name', 'url']]
            empty_patterns_df = pd.DataFrame(index=courses_df.index, columns=['matched'] + ACCEPTED_LANGUAGES)
            courses_df = pd.concat((courses_df['name'], empty_patterns_df, courses_df['url']), axis=1)
            courses_df['matched'] = 0

            # For each matched courses in the matched dictionary, get the matched patterns in each language
            for courses_id_name in matches_json.keys():
                course_id = courses_id_name.split(':')[0]
                for lang in matches_json[courses_id_name].keys():
                    courses_df.loc[course_id, lang] = " // ".join(list(matches_json[courses_id_name][lang].keys()))
                    courses_df.loc[course_id, 'matched'] = 1
            print(courses_df)
            # Write output
            courses_df.to_excel(writer, sheet_name=school)


def get_number_of_matches_per_pattern(schools, dictionary_name, scoring_folder=SCORING_OUTPUT_FOLDER):
    """
    TODO:
     - output a file with number of matches for each pattern per uni and total
    """

    # Get all matching files
    matches_json_dict = dict.fromkeys(schools)
    for school in schools:
        matches_fn = Path(os.path.abspath('')).parent.absolute().joinpath(
            f"../{scoring_folder}{school}_matches_{YEAR}.json")
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
            print(school)
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
    fn = f"/home/duboisa1/shifters/Education4Climate/data/scoring-analysis/" \
         f"number_matches_per_pattern_{dictionary_name}.xlsx"
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
            school_df = pd.read_excel(open(input_fn, 'rb'), sheet_name=school)
            # Remove course that do not have the pattern
            school_df = school_df.dropna(subset=["fr"])
            school_df = school_df[school_df["fr"].apply(lambda x: any([i == pattern for i in x.split(" // ")]))]
            print(school_df)
            # Rearrange columns
            if len(school_df) != 0:
                school_df = school_df[['id', 'name', 'matched', 'url', 'fr']]
                school_df.to_excel(writer, sheet_name=school)


if __name__ == "__main__":

    schools_ = ["kuleuven", "uantwerpen", "uclouvain", "ugent", "uhasselt",
                "ulb", "uliege", "umons", "unamur", "uslb", "vub"]
    schools_ += ["artevelde", "ecam", "ecsedi-isalt", "ehb", "he-ferrer", "heaj", "hech", "hel", "heldb", "helmo",
                 "henallux", "hepl", "hers", "hogent", "howest", "ichec", "ihecs", "ispg", "issig", "odisee",
                 "thomasmore", "ucll", "vinci", "vives"]

    # schools_ = ["uclouvain", "ulb", "uliege", "umons", "unamur", "uslb"]
    # schools_ = ["ecam", "ecsedi-isalt", "ehb", "he-ferrer", "heaj", "hech", "hel", "heldb", "helmo",
    #             "henallux", "hepl", "hers", "ichec", "ihecs", "ispg", "issig", "vinci"]
    # schools_ = ["uliege"]
    get_number_of_matches_per_pattern(schools_, 'v1.1')
    # get_matched_patterns_per_course(schools_, scoring_folder="/data/scoring-output/")
    # get_concurrent_patterns(schools_, "dumping environnement")
