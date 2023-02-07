# -*- coding: utf-8 -*-
from pathlib import Path
from os import remove

import pandas as pd


import urllib3
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

import logging
logging.getLogger().setLevel(logging.INFO)

BASE_URL = "https://www.heh.be/upload/ects/{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}heh_programs_{YEAR}.json')
COURSES_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}heh_courses_{YEAR}.json')


def download_pdf(pdf_url: str) -> str:

    urllib3.disable_warnings()
    file_path = r"file.pdf"
    with urllib3.PoolManager() as http:
        r = http.request('GET', pdf_url)
        with open(file_path, 'wb') as fout:
            fout.write(r.data)
    return file_path


def extract_content(pdf_url: str) -> str:

    try:
        pdf_path = download_pdf(pdf_url)
        content = extract_text(pdf_path, codec='html')
        remove(pdf_path)
    except PDFSyntaxError:
        return ''
    return content


if __name__ == '__main__':

    courses_df = pd.read_json(open(PROG_DATA_PATH, "r"))[["courses", "courses_names", "courses_urls"]]
    courses_ids_list = courses_df["courses"].sum()
    courses_names_list = courses_df["courses_names"].sum()
    courses_urls_list = courses_df["courses_urls"].sum()

    courses_df = pd.DataFrame({'id': courses_ids_list, 'name': courses_names_list, 'url': courses_urls_list})
    courses_df = courses_df.drop_duplicates(subset='id')
    courses_df = courses_df.set_index("id").sort_index()
    courses_df["year"] = f"{YEAR}-{int(YEAR) + 1}"
    courses_df["languages"] = [[]]*len(courses_df)
    courses_df["teachers"] = [[]]*len(courses_df)
    courses_df["goal"] = ""
    courses_df["activity"] = ""
    courses_df["other"] = ""

    for i, (idx, courses_ds) in enumerate(courses_df.iterrows()):

        if i % 10 == 0:
            print(f"{i}/{len(courses_df)}")
        url = BASE_URL.format(courses_ds['url'])
        courses_df.loc[idx, 'url'] = url
        content = extract_content(url)

        # Keep only part after content description
        content = "\n".join(content.split("Contenu de l'")[1:])
        courses_df.loc[idx, "content"] = content

    courses_df.reset_index().to_json(COURSES_DATA_PATH, orient='records')
