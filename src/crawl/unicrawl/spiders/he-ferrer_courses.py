# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup


BASE_URL = "https://fiches-ue.icampusferrer.eu/etatV2.php?id={}&annee={}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}he-ferrer_programs_{YEAR}.json')
LANGUAGES_DICT = {
    "Français": "fr",
    "FranÃ\x83Â§ais": "fr",
    "Anglais": "en",
    "ANG": "en",
    "N?erlandais": "nl",
    "Néerlandais": "nl",
    "NÃ\x83Â©erlandais": "nl"
}


class HEFERRERCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Haute Ecole Francisco Ferrer
    """
    name = "he-ferrer-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}he-ferrer_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_list = sorted(list(set(courses.sum())))

        for course in courses_list:

            yield scrapy.Request(url=BASE_URL.format(course, YEAR),
                                 callback=self.parse_ue,
                                 cb_kwargs={"ue_id": course})

    @staticmethod
    def parse_ue(response, ue_id):

        ue_name = response.xpath("//h3/text()").get()
        year = response.xpath("//h5[1]/text()").get().split(":")[1].strip(" ")

        teachers = response.xpath("//td[contains(text(), \"Responsable de l'UE\")]//following::span[1]/text()").getall()
        teachers = [" ".join(teacher.split(" ")[1:]) + " " + teacher.split(" ")[0] for teacher in teachers]
        teachers = [t.title() for t in teachers]

        ects = response.xpath("//td[contains(text(), 'Crédits ECTS')]//following::strong[1]/text()").get()
        ects = int(ects.strip(" "))

        languages = response.xpath("//td[contains(text(), \"Langue d'enseignement et d'évaluation\")]"
                                   "//following::strong[1]/text()").get()
        languages = [LANGUAGES_DICT[language.strip(" ")] for language in languages.split("/")]
        languages = ["fr"] if len(languages) == 0 else languages

        content = cleanup(response.xpath("//h3[contains(text(), '2')]"
                                         "/following::div[@id='ue_objectifs_wrapper'][1]").get())

        yield {
            "id": ue_id,
            "name": ue_name,
            "year": year,
            "languages": languages,
            "teachers": teachers,
            "ects": [ects],
            "url": response.url,
            "content": content,
            "goal": '',
            "activity": '',
            "other": ''
        }
