# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URl = "https://directory.unamur.be/teaching/courses/{}/{}"  # first format is code course, second is year
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}unamur_programs_{YEAR}.json')

LANGUAGES_DICT = {"Français": 'fr',
                  "Anglais / English": 'en',
                  "Allemand / Deutsch": 'de',
                  "Néerlandais / Nederlands": 'nl',
                  "Italien": "it",
                  "Espagnol / Español": "es"}


class UNamurCourseSpider(scrapy.Spider, ABC):
    name = "unamur-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}unamur_courses_{YEAR}.json')
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URl.format(course_id, YEAR), self.parse_main)

    @staticmethod
    def parse_main(response):
        name_and_id = response.xpath("//h1/text").get()
        name = name_and_id.split("[")[0].strip(" ")
        course_id = name_and_id.split("[")[1].strip("]")

        years = cleanup(response.xpath("//div[@class='foretitle']").get()).strip("Cours ")
        teachers = cleanup(response.xpath("//div[contains(text(), 'Enseignant')]/a").getall())
        teachers = [teacher.replace(' (suppléant)', '') for teacher in teachers]

        languages = cleanup(response.xpath("//div[contains(text(), 'Langue')]").getall())
        languages = [lang.split(":  ")[1] for lang in languages]
        languages = [LANGUAGES_DICT[lang] for lang in languages]

        content = cleanup(response.xpath("//div[@id='tab-introduction']").get())

        # TODO: remove if not required anymore
        # cycle_ects = cleanup(response.xpath("//div[@id='tab-studies']/table/tbody//td").getall())
        # cycles = []
        # ects = []
        # programs = []
        # for i, el in enumerate(cycle_ects):
        #     if i % 3 == 0:
        #         programs += [el]
        #         if "Bachelier" in el:
        #             cycles += ["bac"]
        #         elif "Master" in el:
        #             cycles += ["master"]
        #         else:
        #             cycles += ["other"]
        #     elif i % 3 == 2:
        #         ects += [int(el)]

        # ODO: need to check if there are not sometimes several campuses or faculties
        # organisation = response.xpath("//div[@id='tab-practical-organisation']").get()
        # campus = ''
        # if "Lieu de l'activité" in organisation:
        #     campus = cleanup(
        #         organisation.split("Lieu de l'activité")[1].split("Faculté organisatrice")[0])
        # faculty = cleanup(organisation.split("Faculté organisatrice")[1].split("<br>")[0])

        data = {
            'id': course_id,
            'name': name,
            'year': years,
            'teachers': teachers,
            'languages': languages,
            # 'cycle': cycles,
            # 'ects': ects,
            'url': response.url,
            # 'faculty': faculty,
            # 'campus': campus,
            # 'program': programs,
            'content': content
        }
        yield data
