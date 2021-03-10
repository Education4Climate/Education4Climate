import unittest
import pandas as pd
import glob


class TestTypesFieldsInCrawledFiles(unittest.TestCase):

    def test_courses_and_programs_can_be_read_as_pandas_dataframes(self):
        for file in glob.glob("data/crawling-output/*.json"):
            try:
                pd.read_json(file)
            except Exception as e:
                self.fail("The following exception: {exception}\n"
                          "has been thrown on this file: {file}".format(exception=e, file=file))

    """
    def test_field_names(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
    """


if __name__ == '__main__':
    unittest.main()
