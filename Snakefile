from settings import *

CRAWLERS_FOLDER = 'src/crawl/unicrawl/spiders/'
SRC_SCORE_FOLDER = 'src/score/'
SRC_CRAWL_FOLDER = 'src/crawl/'
SRC_WEB_FOLDER = 'src/web/'
# CRAWLING_OUTPUT_FOLDER = 'data/crawling-output/'
# SCORING_OUTPUT_FOLDER = 'data/scoring-output/'
# WEB_INPUT_FOLDER = 'src/web-ui/data/'
# YEAR = 2020

# TODO: add special rules when merge is needed -> expl UCLouvain

wildcard_constraints:
    year="[0-9]*",
    school="[-a-zA-Z]*",
    special_schools="uclouvain"

schools = ["vub", "kuleuven", "uliege", "umons", "unamur"]

ruleorder: merge_duplicates > crawl_programs

# All school rules
rule score_programs_for_all_school:
    input: expand(SCORING_OUTPUT_FOLDER + '{school}_programs_scoring_{year}.csv', school=schools, year=YEAR)

rule score_courses_for_all_school:
    input: expand(SCORING_OUTPUT_FOLDER + '{school}_scoring_{year}.csv', school=schools, year=YEAR)

rule crawl_programs_for_all_school:
    input: expand(CRAWLING_OUTPUT_FOLDER + '{school}_programs_{year}.csv', school=schools, year=YEAR)

rule crawl_courses_for_all_school:
    input: expand(CRAWLING_OUTPUT_FOLDER + '{school}_courses_{year}.csv', school=schools, year=YEAR)

rule prepare_to_web_for_all_school:
    input:
        expand(WEB_INPUT_FOLDER + '{school}_data_{year}_light.csv', school=schools, year=YEAR),
        expand(WEB_INPUT_FOLDER + '{school}_data_{year}_programs.csv', school=schools, year=YEAR)

# Per school rule
rule crawl_programs:
    output: CRAWLING_OUTPUT_FOLDER + '{school}_programs_{year}.json'
    shell:
        "python -m scrapy.cmdline runspider {CRAWLERS_FOLDER}{wildcards.school}_programs.py"

rule crawl_programs_with_duplicates:
    output: CRAWLING_OUTPUT_FOLDER + 'uclouvain_programs_{year}_pre.json'
    shell:
        "python -m scrapy.cmdline runspider {CRAWLERS_FOLDER}uclouvain_programs.py"

# TODO: probably need to update with ugent
rule merge_duplicates:
    input: CRAWLING_OUTPUT_FOLDER + 'uclouvain_programs_{year}_pre.json'
    output: CRAWLING_OUTPUT_FOLDER + 'uclouvain_programs_{year}.json'
    shell:
        "python {SRC_CRAWL_FOLDER}merge_programs.py -s uclouvain -y {wildcards.year}"


rule crawl_courses:
    input: CRAWLING_OUTPUT_FOLDER + '{school}_programs_{year}.json'
    output: CRAWLING_OUTPUT_FOLDER + '{school}_courses_{year}.json'
    shell:
        "python -m scrapy.cmdline runspider {CRAWLERS_FOLDER}{wildcards.school}_courses.py"

rule score_courses:
    input: CRAWLING_OUTPUT_FOLDER + '{school}_courses_{year}.json'
    output:
        SCORING_OUTPUT_FOLDER + '{school}_scoring_{year}.csv',
        SCORING_OUTPUT_FOLDER + '{school}_matches_{year}.json'
    shell:
        "python {SRC_SCORE_FOLDER}courses.py -s {wildcards.school} -y {wildcards.year}"

rule score_programs:
    input:
        CRAWLING_OUTPUT_FOLDER + '{school}_programs_{year}.json',
        SCORING_OUTPUT_FOLDER + '{school}_scoring_{year}.csv'
    output: SCORING_OUTPUT_FOLDER + '{school}_programs_scoring_{year}.csv'
    shell:
        "python {SRC_SCORE_FOLDER}programs.py -s {wildcards.school} -y {wildcards.year}"


rule prepare_to_web:
    input:
        CRAWLING_OUTPUT_FOLDER + '{school}_courses_{year}.json',
        CRAWLING_OUTPUT_FOLDER + '{school}_programs_{year}.json',
        SCORING_OUTPUT_FOLDER + '{school}_scoring_{year}.csv',
        SCORING_OUTPUT_FOLDER + '{school}_programs_scoring_{year}.csv'
    output:
        WEB_INPUT_FOLDER + '{school}_data_{year}_light.csv',
        WEB_INPUT_FOLDER + '{school}_data_{year}_heavy.csv',
        WEB_INPUT_FOLDER + '{school}_data_{year}_programs.csv'
    shell:
        "python {SRC_WEB_FOLDER}prepare.py -s {wildcards.school} -y {wildcards.year}"