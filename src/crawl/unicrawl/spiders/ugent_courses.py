# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from config.settings import YEAR
from config.utils import cleanup

BASE_URl = "https://studiegids.ugent.be/2020/NL/studiefiches/{}.pdf"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../data/crawling-output/ugent_programs_{YEAR}.json')

# TODO: check languages
LANGUAGES_DICT = {"Nederlands": 'nl',
                  "Dutch": 'nl',
                  "Frans": 'fr',
                  "French": 'fr',
                  "Français": 'fr',
                  "Engels": 'en',
                  "English": 'en',
                  "Deutsch": 'de',
                  "German": 'de',
                  "Duits": 'de',
                  "Spanish": 'es',
                  "Spaans": 'es',
                  "Español": 'es',
                  "Italian": 'it',
                  "Italiaans": 'it',
                  "Italiano": 'it',
                  "Polish": 'pl',
                  "Pools": 'pl',
                  "Russisch": 'ru',
                  "Arabic": 'ar',
                  "Arabisch": 'ar',
                  "Japans": 'jp',
                  "Chinees": 'cn',
                  'Korean': 'kr'}


class UGentCourseSpider(scrapy.Spider, ABC):
    name = "ugent-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../data/crawling-output/ugent_courses_{YEAR}.json')
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        print(len(courses_ids_list))
        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URl.format(course_id), self.parse_main, cb_kwargs={'course_id': course_id})

    @staticmethod
    def parse_main(response, course_id):



        yield {
            'id': course_id,
            'name': course_name,
            'year': years,
            'teacher': teachers,
            'language': languages,
            'content': content,
            'url': response.url
        }
