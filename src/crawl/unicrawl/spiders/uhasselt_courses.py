from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from config.utils import cleanup
from config.settings import YEAR

BASE_URL = "https://uhintra03.uhasselt.be/studiegidswww/opleidingsonderdeel.aspx?a={}&i={}"
PROG_DATA_PATH = Path(f'../../data/crawling-output/uhasselt_programs_{YEAR}.json')
LANGUAGE_DICT = {}


class UHasseltCourseSpider(scrapy.Spider, ABC):
    name = "uhasselt-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/uhasselt_courses_{YEAR}.json',
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URL.format(course_id, YEAR), self.parse_main)

    @staticmethod
    def parse_main(response):

        data = {
            'id': short_name,
            'name': class_name,
            'year': years,
            'teacher': teachers,
            'language': languages,
            'url': response.url,
            'content': content,
        }

        yield data
