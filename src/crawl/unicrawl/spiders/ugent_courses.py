# -*- coding: utf-8 -*-
from pathlib import Path
from abc import ABC
from os import remove

import pandas as pd

import scrapy

import urllib3
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

import logging
logging.getLogger().setLevel(logging.INFO)

BASE_URL = "https://studiekiezer.ugent.be/ministudiefiche/{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}ugent_programs_{YEAR}.json')


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
        content = extract_text(pdf_path)
        remove(pdf_path)
    except PDFSyntaxError:
        return ''
    return content


class UGentCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for UGent
    """

    name = 'ugent-courses'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ugent_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_df = pd.read_json(open(PROG_DATA_PATH, "r"))[["courses", "courses_names",
                                                              "courses_languages", "courses_urls"]]
        courses_ids_list = courses_df["courses"].sum()
        courses_names_list = courses_df["courses_names"].sum()
        courses_lang_list = courses_df["courses_languages"].sum()
        courses_urls_list = courses_df["courses_urls"].sum()

        courses_df = pd.DataFrame({'id': courses_ids_list, 'name': courses_names_list,
                                   'languages': courses_lang_list, 'url': courses_urls_list})
        courses_df = courses_df.drop_duplicates(subset='id')

        for _, courses_ds in courses_df.iterrows():
            languages = courses_ds['languages'].split(',')
            languages = [] if languages == [''] else languages
            yield scrapy.Request(url=BASE_URL.format(courses_ds['url']),
                                 callback=self.parse_course_info,
                                 cb_kwargs={"course_id": courses_ds['id'],
                                            "course_name": courses_ds['name'],
                                            "languages": languages})

    @staticmethod
    def parse_course_info(response, course_id, course_name, languages):

        response_json = response.json()
        teachers = []
        if 'lesgever' in response_json:
            teachers = [response_json['lesgever']]
        else:
            print(course_name)
            print(response_json)
        teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]
        # Course description
        if 'studieficheUrlNL' in response_json:
            content_link = response_json['studieficheUrlNL']
            content = extract_content(content_link)
        else:
            content_link = response.url
            content = ''

        yield {
            "id": course_id,
            "name": course_name,
            "year": f"{YEAR}-{int(YEAR) + 1}",
            "languages": languages,
            "teachers": teachers,
            "url": content_link,
            "content": content,
            "goal": '',
            "activity": '',
            "other": ''
        }
