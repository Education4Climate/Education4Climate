import unittest
import pandas as pd
import glob
import sys
from typing import List

REQUIRED_COLUMNS_COURSES = {"name", "id", "teachers", "ects", "content", "cycle", "languages", "url", "year", "campus",
                            "faculty", "program"}
REQUIRED_COLUMNS_PROGRAMS = {"name", "id", "cycle", "campus", "faculty", "courses", "ects"}

TYPES_COLUMNS_COURSES = {"name": str, "id": str, "teachers": list, "content": str,
                         "languages": list, "url": str, "year": str}

TYPES_COLUMNS_PROGRAMS = {"name": str, "id": str, "cycle": str, "campus": str, "faculty": str, "courses": list,
                          "ects": list}


class TestTypesFieldsInCrawledFiles(unittest.TestCase):

    def test_courses_and_programs_can_be_read_as_pandas_dataframes(self):
        for file in glob.glob("data/crawling-output/*.json"):
            try:
                pd.read_json(file)
            except Exception as e:
                self.fail("The following exception: {exception}\n"
                          "has been thrown on this file: {file}".format(exception=e, file=file))

    """
    def test_required_columns_are_in_course_files(self):
        for file in glob.glob("data/crawling-output/*_courses_*.json"):
            with self.subTest(file=file):
                columns = set(pd.read_json(file).columns)
                self.assertTrue(REQUIRED_COLUMNS_COURSES.issubset(columns),
                                msg="\n\nThe following columns are missing in the file >>> {file} <<<\n"
                                    "====> {missing_columns}".format(file=file,
                                                                     missing_columns=REQUIRED_COLUMNS_COURSES.difference(
                                                                         columns)))

    def test_required_columns_are_in_program_files(self):
        for file in glob.glob("data/crawling-output/*_programs_*.json"):
            with self.subTest(file=file):
                columns = set(pd.read_json(file).columns)
                self.assertTrue(REQUIRED_COLUMNS_PROGRAMS.issubset(columns),
                                msg="\n\nThe following columns are missing in the file >>> {file} <<<\n"
                                    "====> {missing_columns}".format(file=file,
                                                                     missing_columns=REQUIRED_COLUMNS_PROGRAMS.difference(
                                                                         columns)))
    """


    """
    def test_too_many_columns_in_program_files(self):
        for file in glob.glob("data/crawling-output/*_programs_*.json"):
            with self.subTest(file=file):
                columns = set(pd.read_json(file).columns)
                self.assertTrue(REQUIRED_COLUMNS_PROGRAMS.issubset(columns),
                                msg="\n\nThe following columns are not required in the file >>> {file} <<<\n"
                                    "====> {not_required_columns}".format(file=file,
                                                                          not_required_columns=columns.difference(
                                                                              REQUIRED_COLUMNS_PROGRAMS)))

    def test_too_many_columns_in_course_files(self):
        for file in glob.glob("data/crawling-output/*_courses_*.json"):
            with self.subTest(file=file):
                columns = set(pd.read_json(file).columns)
                self.assertTrue(REQUIRED_COLUMNS_COURSES.issubset(columns),
                                msg="\n\nThe following columns are not required in the file >>> {file} <<<\n"
                                    "====> {not_required_columns}".format(file=file,
                                                                          not_required_columns=columns.difference(
                                                                              REQUIRED_COLUMNS_COURSES)))
    """

    def test_types_in_program_files(self):
        for file in [f for f in glob.glob("data/crawling-output/*_programs_*.json") if "courses" not in f]:
            with self.subTest(file=file):
                data = pd.read_json(file)
                for column in data.columns:
                    with self.subTest(column=column):
                        for value in data[column].values:
                            self.assertTrue(type(value) == TYPES_COLUMNS_PROGRAMS[column],
                                            msg="\n\nIn the column  of the file {file}"
                                                "\nThe expecting type of '{column}' is >> {exp_type} << "
                                                "but a value with type >> {act_type} << "
                                                "has been found".format(column=column,
                                                                        file=file,
                                                                        exp_type=TYPES_COLUMNS_PROGRAMS[column],
                                                                        act_type=type(value)))

    def test_types_in_course_files(self):
        for file in [f for f in glob.glob("data/crawling-output/*_courses_*.json") if "programs" not in f]:
            with self.subTest(file=file):
                data = pd.read_json(file)
                for column in data.columns:
                    with self.subTest(column=column):
                        for i, value in enumerate(data[column].values):
                            self.assertTrue(type(value) == TYPES_COLUMNS_COURSES[column],
                                            msg="\n\nIn the column  of the file {file}"
                                                "\nThe expecting type of '{column}' is >> {exp_type} << "
                                                "but a value with type >> {act_type} << "
                                                "has been found.\nline: {line} - value: {value}".format(column=column,
                                                                        file=file,
                                                                        exp_type=TYPES_COLUMNS_COURSES[column],
                                                                        act_type=type(value),
                                                                        line=i,
                                                                        value=value))


if __name__ == '__main__':
    unittest.main()
