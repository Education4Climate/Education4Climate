# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from config.utils import cleanup
from config.settings import YEAR

BASE_URl = "https://www.ecam.be/{}"  # first format is code course, second is year
PROG_DATA_PATH = Path(f'../../data/crawling-output/ecam_programs_{YEAR}.json')

# TODO: checker langues
LANGUAGES_DICT = {"FR": 'fr', "EN": 'en'}


class ECAMCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for ECAM Bruxelles
    """

    name = "ecam-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/ecam_courses_{YEAR}.json',
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            base_dict = {"id": course_id}
            yield scrapy.Request(BASE_URl.format(course_id), self.parse_main, cb_kwargs={"base_dict": base_dict})
            break

    @staticmethod
    def parse_main(response, base_dict):

        name = response.xpath("//th[text()=\"Nom de l'UE\"]/following::td[1]/text()").get()[7:]
        years = response.xpath("//div[contains(text(), 'Année académique')]"
                               "/text()").get().split('académique ')[1].split(" - ")[0]
        teachers = response.xpath("//th[text()=\"Responsable\"]/following::td[1]/text()").get()
        languages = response.xpath("//th[text()=\"Langue\"]/following::td[1]/text()").get()
        languages = [LANGUAGES_DICT[lang] for lang in languages.split(" ")]

        # TODO
        content = ""

        cur_dict = {
            'name': name,
            'year': years,
            'teacher': teachers,
            'language': languages,
            'content': content,
            'url': response.url,
        }
        yield {**base_dict, **cur_dict}
