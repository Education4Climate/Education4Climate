import json
import pandas as pd
from typing import List

UGENT_CRAWLED_PATH = 'data/crawling-output/ugent_courses_and_programs_2020.json'
UGENT_NEW_CRAWLED_PATH_PROGRAMS = 'data/crawling-output/ugent_programs_2020.json'
UGENT_NEW_CRAWLED_PATH_COURSES = 'data/crawling-output/ugent_courses_2020.json'


def main():
    # Loading data
    data = pd.read_json(path_or_buf=UGENT_CRAWLED_PATH)

    # Replacing NaN values in the column 'courses' to empty lists [] in order to concatenate the courses
    for field in ["courses", "courses_teacher", "courses_ects", "courses_content"]:
        for row in data.loc[data[field].isnull(), field].index:
            data.at[row, field] = []

    # Generating programs file
    programs_and_courses_data = data.groupby(["id", "name", "cycle", "url"]).agg({"courses": sum,
                                                                      "courses_teacher": sum,
                                                                      "courses_ects": sum,
                                                                      "courses_content": sum
                                                                      }).reset_index()
    #print(programs_and_courses_data)
    PROGRAM_COLUMNS = ["id", "name", "cycle", "url", "courses"]
    programs_and_courses_data[PROGRAM_COLUMNS].to_json(path_or_buf=UGENT_NEW_CRAWLED_PATH_PROGRAMS, orient='records')

    # Generating courses file
    courses_columns = [col for col in data.columns if col.startswith('courses')]
    courses_data = []
    for program_row in programs_and_courses_data.iterrows():
        if program_row[1]['courses']:
            for i in range(len(program_row[1]['courses'])):
                course_row = [program_row[1][col][i] for col in courses_columns]
                courses_data.append(course_row)

    new_columns = [col.removeprefix('courses_') for col in data.columns if col.startswith("courses")]
    print("new_columns: {}".format(new_columns))
    courses_df = pd.DataFrame(columns=new_columns,
                              data=courses_data)
    print(courses_df)
    courses_df.to_json(path_or_buf=UGENT_NEW_CRAWLED_PATH_COURSES, orient='records')


if __name__ == "__main__":
    main()
