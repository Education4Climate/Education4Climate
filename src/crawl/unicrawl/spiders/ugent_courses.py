# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path
from os import remove
import json

import numpy as np
import pandas as pd
import scrapy

import urllib3
from pdfminer.high_level import extract_text


from config.settings import YEAR

BASE_URl = "https://studiegids.ugent.be/2020/NL/studiefiches/{}.pdf"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../data/crawling-output/ugent_programs_{YEAR}.json')


def download_pdf(pdf_url: str) -> str:
    urllib3.disable_warnings()
    filePath = r"file.pdf"
    with urllib3.PoolManager() as http:
        r = http.request('GET', pdf_url)
        with open(filePath, 'wb') as fout:
            fout.write(r.data)
    return filePath


def extract_content(pdf_url: str) -> str:
    pdf_path = download_pdf(pdf_url)
    content = extract_text(pdf_path)
    remove(pdf_path)
    return content


def main(fn):

    courses_df = pd.read_json(open(PROG_DATA_PATH, "r"))[["courses", "courses_names", "courses_teachers"]]
    courses_ids_list = courses_df['courses'].sum()
    courses_names_list = courses_df['courses_names'].sum()
    courses_teachers_list = courses_df['courses_teachers'].sum()
    unique_courses_ids_list = sorted(list(set(courses_ids_list)))

    data = []
    for i, course_id in enumerate(unique_courses_ids_list):
        if i % 10 == 0:
            print(course_id, f'{i}/{len(unique_courses_ids_list)}')
        courses_ids_positions = [i for i, c in enumerate(courses_ids_list) if c == course_id]
        # Find name of the course
        course_name = np.array(courses_names_list)[courses_ids_positions][0]
        # Find teachers giving the course
        unique_teachers = list(set(np.array(courses_teachers_list)[courses_ids_positions]))
        unique_teachers = [t for t in unique_teachers if t is not None and 'N.' not in t]
        # Languages
        languages = ['nl']
        if '[' in course_name and ']' in course_name:
            languages = course_name.split("[")[-1].split(']')[0].split(',')
        # Content
        url = BASE_URl.format(course_id)
        content = extract_content(url)

        data += [{
            'id': course_id,
            'name': course_name,
            'year': f"{YEAR}-{int(YEAR) + 1}",
            'teachers': unique_teachers,
            'languages': languages,
            'url': url,
            'content': content
        }]

    data = pd.DataFrame.from_dict(data)
    data.to_json(fn, orient='records')


if __name__ == '__main__':
    FEED_URI = Path(__file__).parent.absolute().joinpath(f'../../../../data/crawling-output/ugent_courses_{YEAR}.json')
    main(FEED_URI)
