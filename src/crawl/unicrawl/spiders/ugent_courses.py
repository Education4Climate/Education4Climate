# -*- coding: utf-8 -*-
from pathlib import Path
from abc import ABC
from os import remove

import pandas as pd

import scrapy

import urllib3
from pdfminer.high_level import extract_text

from settings import YEAR, CRAWLING_OUTPUT_FOLDER


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
    pdf_path = download_pdf(pdf_url)
    content = extract_text(pdf_path)
    remove(pdf_path)
    return content


class UGentCourseSpider(scrapy.Spider, ABC):
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

        courses_list = list(set(zip(courses_ids_list, courses_names_list, courses_lang_list, courses_urls_list)))

        for course_id, course_name, course_lang, course_url in courses_list:
            yield scrapy.Request(url=BASE_URL.format(course_url),
                                 callback=self.parse_course_info,
                                 cb_kwargs={"course_id": course_id,
                                            "course_name": course_name,
                                            "language": course_lang})

    def parse_course_info(self, response, course_id, course_name, language):

        response_json = response.json()
        teacher = response_json['lesgever']
        # Course description
        content_link = response_json['studieficheUrlNL']
        content = extract_content(content_link)

        yield {
            "id": course_id,
            "name": course_name,
            "year": f"{YEAR}-{int(YEAR) + 1}",
            "languages": [language],
            "teachers": [teacher],
            "url": content_link,
            "content": content,
            "goal": '',
            "activity": '',
            "other": ''
        }
