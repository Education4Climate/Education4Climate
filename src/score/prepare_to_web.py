import pandas as pd
import json
import argparse

import config.settings as s

def main(args):
    scores = pd.read_csv(s.SCORING_OUTPUT_FOLDER + args.school + '_scoring_' + args.year + '.csv')
    scores = scores.drop(columns=["class", "teachers"]).rename(columns={"code": "id"})
    js = json.load(open(s.CRAWLING_OUTPUT_FOLDER + args.school + "_courses_" + args.year + ".json"))
    courses = pd.DataFrame.from_dict(js)
    courses = courses.rename(
        columns={"anacs": "year", "class": "name", "teachers": "teacher", "shortname": "id", "location": "campus"})
    join = courses.set_index("id").join(scores.set_index("id"), on="id", how="right")
    join.to_csv(s.WEB_INPUT_FOLDER + args.school + '_data_' + args.year + '_heavy.csv')
    join[join["shift_score"] != 0].to_csv(s.WEB_INPUT_FOLDER + args.school + '_data_' + args.year + '_light.csv')


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--school", help="input json file path")
    parser.add_argument("-y", "--year", help="academic year",default=2020)
    arguments = parser.parse_args()
    main(arguments)

