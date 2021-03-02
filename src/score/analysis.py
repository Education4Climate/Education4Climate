from typing import List

import pandas as pd

from config.settings import SCORING_OUTPUT_FOLDER, CRAWLING_OUTPUT_FOLDER


def analyse_courses(schools: List[str], year: int, themes: List[str]):

    number_of_courses_per_school = pd.Series(index=schools, dtype=int)
    number_of_matched_courses_per_theme = pd.DataFrame(index=schools, columns=themes, dtype=int)
    number_of_matched_courses_in_any_theme = pd.Series(0., index=schools, dtype=int)

    for school in schools:
        # Read score for school
        courses_scores = pd.read_csv(f"../../{SCORING_OUTPUT_FOLDER}{school}_scoring_{year}.csv", index_col=0)
        number_of_courses_per_school[school] = len(courses_scores)
        number_of_matched_courses_per_theme.loc[school] = courses_scores.sum(axis=0)
        number_of_matched_courses_in_any_theme[school] += courses_scores.max(axis=1).sum()

    print(f"\nNumber of courses per school\n{number_of_courses_per_school}")
    print(f"\nNumber of matched courses per theme\n{number_of_matched_courses_per_theme.astype(int)}")
    perc_of_matched_course_per_theme = number_of_matched_courses_per_theme.div(number_of_courses_per_school, axis=0)*100
    print(f"\nPercentage of matched courses per theme\n{perc_of_matched_course_per_theme.round(2)}")
    print(f"\nNumber of matched courses in any theme\n{number_of_matched_courses_in_any_theme}")
    perc_of_matched_course_in_any_theme = number_of_matched_courses_in_any_theme*100/number_of_courses_per_school
    print(f"\nPercentage of matched courses in any theme\n{perc_of_matched_course_in_any_theme.round(2)}")

    return 0


def analyse_programs(schools: List[str], year: int, themes: List[str]):

    number_of_programs_per_school = pd.Series(index=schools, dtype=int)
    number_of_matched_programs_per_theme = pd.DataFrame(index=schools, columns=themes, dtype=int)
    number_of_matched_programs_in_any_theme = pd.Series(0., index=schools, dtype=int)
    avg_perc_of_matched_courses_per_program_per_theme = pd.DataFrame(index=schools, columns=themes, dtype=int)

    for school in schools:
        # Read score for school
        programs_scores = pd.read_csv(f"../../{SCORING_OUTPUT_FOLDER}{school}_programs_scoring_{year}.csv", index_col=0)
        number_of_programs_per_school[school] = len(programs_scores)
        number_of_matched_programs_per_theme.loc[school] = programs_scores.apply(lambda x: x > 0).sum(axis=0)
        number_of_matched_programs_in_any_theme[school] = programs_scores.apply(lambda x: x > 0).max(axis=1).sum()

        # Get number of courses per program (that have at least one matched course)
        programs_info = pd.read_json(f"../../{CRAWLING_OUTPUT_FOLDER}{school}_programs_{year}.json").set_index("id")
        number_of_courses_per_program = programs_info['courses'].apply(lambda x: len(x))
        for theme in themes:
            matched_programs = programs_scores[programs_scores[theme] > 0].index
            matched_programs_scores = programs_scores.loc[matched_programs, theme]
            matched_programs_number_of_courses = number_of_courses_per_program[matched_programs]
            avg_perc_of_matched_courses_per_program_per_theme.loc[school, theme] = \
                (matched_programs_scores.div(matched_programs_number_of_courses, axis=0)).median(axis=0)

    print(f"\nNumber of programs per school\n{number_of_programs_per_school}")
    print(f"\nNumber of matched programs per theme\n{number_of_matched_programs_per_theme.astype(int)}")
    perc_of_matched_programs_per_theme = \
        number_of_matched_programs_per_theme.div(number_of_programs_per_school, axis=0)*100
    print(f"\nPercentage of matched programs per theme\n{perc_of_matched_programs_per_theme.round(2)}")
    print(f"\nNumber of matched programs in any theme\n{number_of_matched_programs_in_any_theme}")
    perc_of_matched_programs_in_any_theme = number_of_matched_programs_in_any_theme*100/number_of_programs_per_school
    print(f"\nPercentage of matched programs in any theme\n{perc_of_matched_programs_in_any_theme.round(2)}")
    print(f"\nMedian percentage of matched courses per program (that had at least one matched course)"
          f"\n{avg_perc_of_matched_courses_per_program_per_theme.round(4)*100}")


if __name__ == '__main__':
    schools_ = ["ucl", "uliege", "ulb", "umons", "unamur"]
    themes_ = ["climatology", "decarbonization", "durability", "energy", "environment", "society"]
    analyse_courses(schools_, 2020, themes_)
    analyse_programs(schools_, 2020, themes_)
