import pandas as pd
import json

# TODO: Improve the code, I just made it work for the UCL case
def main():
    scores = pd.read_csv('data/score_results/ucl_scoring_2020.csv')
    scores = scores.drop(columns=["class", "teachers"]).rename(columns={"code": "id"})
    js = json.load(open("data/crawling-results/ucl_courses_2020.json"))
    courses = pd.DataFrame.from_dict(js)
    courses = courses.rename(
        columns={"anacs": "year", "class": "name", "teachers": "teacher", "shortname": "id", "location": "campus"})
    join = courses.set_index("id").join(scores.set_index("id"), on="id", how="right")
    join.to_csv('data/web-ui_inputs/ucl_data_2020_heavy.csv')
    join[join["shift_score"] != 0].to_csv('data/web-ui_inputs/ucl_data_2020_light.csv')


if __name__=="__main__":
    main()

