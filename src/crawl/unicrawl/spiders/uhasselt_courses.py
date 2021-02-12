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

        i = 0
        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URL.format(course_id, YEAR), self.parse_main)
            if i == 4:
                return
            i += 1

    # TODO: need to do a POST request too?

    @staticmethod
    def parse_main(response):

        id = ''
        course_name = ''
        year = ''
        teachers = response.xpath("//td[contains(text(), 'lecturer')]/following::td[1]/a/text()").getall()
        teachers += response.xpath("//td[contains(text(), 'lecturer')]/following::td[1]/a/text()").getall()
        languages = ''
        content = ''

        data = {
            'id': id,
            'name': course_name,
            'year': year,
            'teacher': teachers,
            'language': languages,
            'url': response.url,
            'content': content,
        }

        yield data
