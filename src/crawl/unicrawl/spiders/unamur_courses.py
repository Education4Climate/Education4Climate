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
            f'../../../../{CRAWLING_OUTPUT_FOLDER}unamur_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URl.format(course_id, YEAR), self.parse_main,
                                 cb_kwargs={'course_id': course_id})

    @staticmethod
    def parse_main(response, course_id):

        name_and_id = response.xpath("//h1/text()").get()
        name = name_and_id.split("[")[0].strip(" ")

        years = cleanup(response.xpath("//div[@class='foretitle']").get()).strip("Cours ")
        teachers = cleanup(response.xpath("//div[contains(text(), 'Enseignant')]/a").getall())
        teachers = [teacher.replace(' (suppléant)', '') for teacher in teachers]

        languages = cleanup(response.xpath("//div[contains(text(), 'Langue')]").getall())
        languages = [lang.split(":  ")[1] for lang in languages]
        languages = [LANGUAGES_DICT[lang] for lang in languages]

        # Could not find a way to separate sections # TODO: possible in post-processing ?
        content = cleanup(response.xpath("//div[@id='tab-introduction']").get())

        organisation = response.xpath("//div[@id='tab-practical-organisation']").get()
        campus = 'Namur'
        if "Lieu de l'activité" in organisation:
            campus = cleanup(
                 organisation.split("Lieu de l'activité")[1].split("Faculté organisatrice")[0])
        if campus == 'LOUVAIN-LA-NEUVE':
            campus = 'Louvain-la-Neuve'
        else:
            campus = campus.lower().capitalize()

        yield {
            'id': course_id,
            'name': name,
            'year': years,
            'languages': languages,
            'teachers': teachers,
            'campuses': [campus],
            'url': response.url,
            'content': content,
            'goal': '',
            'activity': '',
            'other': ''
        }
