import glob
import pandas as pd
import json
import os
from collections import defaultdict

from ast import literal_eval
from pathlib import Path

from settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER, PATTERNS_PATH, YEAR, ACCEPTED_LANGUAGES

# TODO noting patterns problems here
# [environnement, durabilite] AND durabilite environnement --> remove one


def get_course_view(file):
    js = json.load(open(file))
    courses = defaultdict(list)
    for pattern_res in js.values():
        for course_id in pattern_res.keys():
            courses[course_id].extend(list(pattern_res[course_id].keys()))
    return courses


def get_patterns_view(file, result_dic):
    js = json.load(open(file))

    for theme, matches in js.items():
        if theme not in result_dic.keys(): result_dic[theme] = {}
        for id, pattern_dict in matches.items():
            for pattern, m in pattern_dict.items():
                if pattern in result_dic[theme].keys():
                    result_dic[theme][pattern]["ids"].append(id)
                    result_dic[theme][pattern]["matches"].extend(m)
                else:
                    result_dic[theme][pattern] = {"ids": [id], "matches": m}
    return result_dic


def get_pattern_matches(file, result_dic):
    js = json.load(open(file))

    for theme, matches in js.items():
        for id, pattern_dict in matches.items():
            for pattern, m in pattern_dict.items():
                if pattern in result_dic.keys():
                    result_dic[pattern]["ids"].append(id)
                    result_dic[pattern]["matches"].extend(m)
                else:
                    result_dic[pattern] = {"ids": [id], "matches": m}
    return result_dic


def old_stuff():
    from sklearn.metrics import classification_report

    UNIF = ["ucl", "ulb"]
    true_pos = json.load(open("../../../data/analysis/fr_true_pos.json"))
    courses_files = glob.glob("../../" + CRAWLING_OUTPUT_FOLDER + "*courses_2020*")
    courses_dic = {x["id"]: x["name"] for f in courses_files for x in json.load(open(f))}
    patterns_list = defaultdict(list)
    js_pattern = json.load(open("../../" + PATTERNS_PATH))
    [patterns_list[theme].append(p) for theme, v in js_pattern.items() for p in v["fr"]]
    [patterns_list[theme].append(p) for theme, v in js_pattern.items() for p in v["en"]]
    [patterns_list[theme].append(p) for theme, v in js_pattern.items() for p in v["nl"]]

    writer = pd.ExcelWriter("../../data/analysis/pattern_comparison.xlsx")
    matching_files = glob.glob("../../" + SCORING_OUTPUT_FOLDER + "*matches_2020*")
    for f in matching_files:
        scoring_file = f.replace("matches_2020.json", "scoring_2020.csv")
        print(f)
        results = {}
        university = os.path.split(f)[-1].replace("_matches_2020.json", "")
        if university in UNIF:
            df = pd.read_csv(scoring_file).dropna(subset=["id"])
            df["total"] = df.iloc[:, 1:].sum(axis=1)
            df["pred"] = df["total"] > 0
            df["gold"] = df["id"].apply(lambda x: True if x in true_pos[university] else False)
            d = get_course_view(f)
            print(df.head())
            for course_id, pattern_matching in d.items():
                tmp = {"name": courses_dic[course_id], "status": "TN"}
                # print(df[df["id"]==course_id])
                tmp.update(df[df["id"] == course_id][["gold", "pred"]].iloc[0].to_dict())

                if tmp["gold"] and tmp["pred"]:
                    tmp["status"] = "TP"
                elif tmp["gold"] and tmp["pred"] is False:
                    tmp["status"] = "FN"
                elif tmp["gold"] is False and tmp["pred"]:
                    tmp["status"] = "FP"
                tmp["patterns"] = pattern_matching
                results[course_id] = tmp

            print(university, classification_report(df["gold"], df["pred"]))
            df = pd.DataFrame.from_dict(results, orient='index')
            df.to_excel(writer, sheet_name="{}_results".format(university))
            pattern_struct = {}
            for id, struct in results.items():
                for pattern in struct["patterns"]:
                    if pattern in pattern_struct.keys():
                        pattern_struct[pattern]["correct"] += int(struct["pred"] and struct["gold"])
                        pattern_struct[pattern]["error"] += int(struct["pred"] and not struct["gold"])
                        pattern_struct[pattern]["combi"] += int(len(struct["patterns"]) > 1)
                    else:
                        pattern_struct[pattern] = {
                            "correct": int(struct["pred"] and struct["gold"]),
                            "error": int(struct["pred"] and not struct["gold"]),
                            "combi": int(len(struct["patterns"]) > 1)
                        }
            df = pd.DataFrame.from_dict(pattern_struct, orient="index")
            df.to_excel(writer, sheet_name="{}_pattern_metrics".format(university))

    writer.close()


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
    fn = "/home/duboisa1/shifters/Education4Climate/data/scoring-analysis/number_matches_per_pattern.xlsx"
    with pd.ExcelWriter(fn) as writer:
        for lang in ACCEPTED_LANGUAGES:
            counting_dict[lang].to_excel(writer, sheet_name=lang)


if __name__ == "__main__":

    schools_ = ["kuleuven", "uantwerpen", "uclouvain", "ugent", "uhasselt",
                "ulb", "uliege", "umons", "unamur", "uslb", "vub"]
    schools_ = ["artevelde", "ecam", "ecsedi-isalt", "ehb", "he-ferrer", "heaj", "hech", "hel", "heldb", "helmo",
                "henallux", "hers", "howest", "ichec", "ihecs", "ispg", "issig", "odisee", "thomasmore", "ucll",
                "vinci", "vives"]
    # get_number_of_matches_per_pattern(schools_, 'sdgs')
    schools_ = ['ulb']
    get_matched_patterns_per_course(schools_, scoring_folder="/data/dictionary-comparison/sdgs/")
