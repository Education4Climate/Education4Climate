import json,re,pandas as pd
from src.score.courses import compute_score
from settings import PATTERNS_PATH,CRAWLING_OUTPUT_FOLDER
import glob
import os
from unidecode import unidecode
from collections import defaultdict
patterns=json.load(open(os.path.join("../../",PATTERNS_PATH)))
patterns_lg=defaultdict(list)
[patterns_lg[l].extend(p) for d in patterns.values() for l,p in d.items()]
courses_files = glob.glob("../../" + CRAWLING_OUTPUT_FOLDER + "*courses_2020*")
courses_desc = {x["id"]: x["content"] for f in courses_files for x in json.load(open(f))}
courses_dic = {x["id"]: x["name"] for f in courses_files for x in json.load(open(f))}

if __name__=="__main__":
    LANG="fr"
    ids=["ARCH-H400",
"ARCH-P7120",
"ARCH-Y500",
"BING-F525",
"CHIM-F430",
"CHIM-H534",
"CNST-H306",
"CNST-P1007",
"CNST-Y512",
"DROI-C5150",
"ELEC-H312",
"ENVI-F452",
"ENVI-F5001",
"GEOG-F203",
"GEOG-F408",
"GEOL-F426",
"GERM-B430",
"GEST-S2002",
"GEST-S204",
"GEST-S407",
"GEST-S454",
"GEST-S471",
"LANG-D314",
"MEDI-J401",
"PHYS-H515",
"POLI-D504",
"PROJ-H404",
"SOCA-D4996",
"TRAN-B2000",
"ECON-S2002",
"GEOG-F102",
"POLI-D434",
"BING-F4001",
"BING-F4003",
"BING-F4004",
"BING-F4005",
"BING-F403",
"BING-F430",
"BING-F523",
"BIOL-F417",
"ENVI-D500",
"TRAD-B4023",
"BING-H5001",
"BIOL-F2001",
"BIOL-F4001",
"CHIM-H504",
"CHIM-H522",
"ECON-S307",
"ENVI-F438",
"MSTL-F604",
"PROJ-H417",
"PROJ-P0602",
"PROJ-P1002",
"URBA-P9009"
        ]

    for id in ids[:2]:
        print(courses_dic[id])
        print(courses_desc[id])
        text=unidecode(courses_dic[id].lower()+"\n"+courses_desc[id].lower())
        print(compute_score(text,patterns_lg[LANG]))

