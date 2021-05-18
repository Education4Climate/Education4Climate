import glob
import pandas as pd
import json,os,re
from collections import defaultdict
from settings import CRAWLING_OUTPUT_FOLDER, SCORING_OUTPUT_FOLDER, PATTERNS_PATH

def get_course_view(file):
    js=json.load(open(file))
    courses=defaultdict(list)
    for pattern_res in js.values():
        for course_id in pattern_res.keys():
            courses[course_id].extend(list(pattern_res[course_id].keys()))
    return courses

def get_patterns_view(file,result_dic):
    js = json.load(open(file))

    for theme, matches in js.items():
        if theme not in result_dic.keys():result_dic[theme]={}
        for id, pattern_dict in matches.items():
            for pattern,m in pattern_dict.items():
                if pattern in result_dic[theme].keys():
                    result_dic[theme][pattern]["ids"].append(id)
                    result_dic[theme][pattern]["matches"].extend(m)
                else:
                    result_dic[theme][pattern]={"ids":[id],"matches":m}
    return result_dic

def get_pattern_matches(file,result_dic):
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


if __name__=="__main__":
    from sklearn.metrics import classification_report
    UNIF=["ucl","ulb"]
    true_pos=json.load(open("../../data/analysis/fr_true_pos.json"))
    courses_files=glob.glob("../../"+CRAWLING_OUTPUT_FOLDER+"*courses_2020*")
    courses_dic = {x["id"]: x["name"] for f in courses_files for x in json.load(open(f))}
    courses_desc = {x["id"]: x["content"] for f in courses_files for x in json.load(open(f))}
    patterns_list = defaultdict(list)
    js_pattern = json.load(open("../../" + PATTERNS_PATH))
    [patterns_list[theme].append(p) for theme, v in js_pattern.items() for p in v["fr"]]
    [patterns_list[theme].append(p) for theme, v in js_pattern.items() for p in v["en"]]
    [patterns_list[theme].append(p) for theme, v in js_pattern.items() for p in v["nl"]]
    writer = pd.ExcelWriter("../../data/analysis/pattern_comparison.xlsx")
    matching_files=glob.glob("../../"+SCORING_OUTPUT_FOLDER+"*matches_2020*")
    for f in matching_files:
        scoring_file=f.replace("matches_2020.json","scoring_2020.csv")
        print(f)
        results = {}
        university=os.path.split(f)[-1].replace("_matches_2020.json","")
        if university in UNIF:
            bad_results={}

            df = pd.read_csv(scoring_file).dropna(subset=["id"])
            df["total"] = df.iloc[:, 1:].sum(axis=1)
            df["pred"] = df["total"] > 0
            df["gold"] = df["id"].apply(lambda x: True if x in true_pos[university] else False)
            d = get_course_view(f)
            print(df.shape,df.head())

            for course_id,pattern_matching in d.items():
                tmp={"name":courses_dic[course_id],"status":"TN"}
                #print(df[df["id"]==course_id])
                tmp.update(df[df["id"]==course_id][["gold","pred"]].iloc[0].to_dict())

                if tmp["gold"] and tmp["pred"]:tmp["status"]="TP"
                #elif tmp["gold"] and tmp["pred"] is False :tmp["status"]="FN"
                elif tmp["gold"] is False and tmp["pred"]:
                    tmp["status"]="FP"
                    bad_results[course_id]={"content":courses_desc[course_id],"patterns":pattern_matching,"status":tmp["status"]}
                tmp["patterns"]=pattern_matching
                results[course_id]=tmp
            for i,r in df.loc[df["gold"] & (df["pred"] ==0)].iterrows():
                tmp={"name":courses_dic[r["id"]],"status":"FN","patterns":[]}
                bad_results[r["id"]]={"content":courses_desc[r["id"]],"patterns":"","status":tmp["status"]}
                results[r["id"]]=tmp

            print(university, classification_report(df["gold"], df["pred"]))
            df=pd.DataFrame.from_dict(results,orient='index')
            with open("../../data/analysis/debug_{}.txt".format(university),"w") as fh_:
                for k,v in bad_results.items():
                    fh_.write("{} ---  {}  ({})\n{}\n{}\n\n\n".format(k,v["status"],courses_dic[k],
                        re.sub("\n[\n \xa0\t]+","\n",v["content"]),v["patterns"]))
                fh_.close()
            df.to_excel(writer,sheet_name="{}_results".format(university))
            pattern_struct={}
            for id,struct in results.items():
                for pattern in struct["patterns"]:
                    if pattern in pattern_struct.keys():
                        pattern_struct[pattern]["correct"]+=int(struct["pred"] and struct["gold"])
                        pattern_struct[pattern]["error"]+=int(struct["pred"] and not struct["gold"])
                        pattern_struct[pattern]["combi"]+=int(len(struct["patterns"])>1)
                    else:pattern_struct[pattern]={
                        "correct":int(struct["pred"] and struct["gold"]),
                        "error":int(struct["pred"] and not struct["gold"]),
                        "combi":int(len(struct["patterns"])>1)
                    }
            df=pd.DataFrame.from_dict(pattern_struct,orient="index")
            df.to_excel(writer,sheet_name="{}_pattern_metrics".format(university))

    writer.close()

