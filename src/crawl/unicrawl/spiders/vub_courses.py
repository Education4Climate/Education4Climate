from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from config.settings import YEAR

BASE_URL = 'https://caliweb.vub.be/?page=course-offer&id={}'
PROG_DATA_PATH = Path(f'../../data/crawling-output/vub_programs_{YEAR}.json')
LANGUAGE_DICT = {"Dutch": 'nl',
                 "Nederlands": 'nl',
                 "English": 'en',
                 "Engels": 'en',
                 "French": 'fr',
                 "Frans": 'fr'}

# Note: need to change the parameter ROBOTS_OBEY in the crawler settings.py to make the crawler work


class VUBCourseSpider(scrapy.Spider, ABC):
    name = "vub-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/vub_courses_{YEAR}.json',
    }

    def start_requests(self):

        # TODO: normallly there can be two versions of the same class,
        #  to be checked if it's necessary to crawl both pages
        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            base_dict = {"id": course_id}
            yield scrapy.Request(BASE_URL.format(course_id), self.parse_course, cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_course(response, base_dict):

        name = response.xpath("//h1/text()").get()
        languages = response.xpath("//dt[text()='Onderwijstaal' or text()='Taught in']"
                                   "/following::dd[1]/text()").getall()
        languages = [LANGUAGE_DICT[lang] for lang in languages]

        teachers = \
            response.xpath("//dt[text()='Onderwijsteam' or text()='Educational team']/following::dd[1]")\
                .get().strip('<dd>').strip("</dd>").replace("(titularis)\n", '').split("<br>")
        teachers = [teacher.strip(" ").strip("\n") for teacher in teachers]
        cur_dict = {"name": name,
                    "language": languages,
                    "teacher": teachers}

        yield {**base_dict, **cur_dict}
