# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = "https://hepl.be/static/{}" + f"-{YEAR}.html"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}hepl_programs_{YEAR}.json')

LANGUAGE_DICT = {
    "Français": "fr",
    "Anglais": "en",
    "English": "en",
    "Allemand": "de",
    "Deutsch": "de",
    "Néerlandais": "nl",
    "Nederlands": "nl",
    "Espagnol": 'es',
    "Español": 'es',
    "Italien": 'it',
    "Italiano": 'it'
}


class HEPLCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for Haute Ecole de la Province de Liège
    """

    name = "hepl-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}hepl_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        ue_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        ue_ids_list = sorted(list(set(ue_ids.sum())))

        for ue_id in ue_ids_list:
            yield scrapy.Request(BASE_URL.format(ue_id), self.parse_ue, cb_kwargs={"ue_id": ue_id})

    @staticmethod
    def parse_ue(response, ue_id):

        ue_name = response.xpath("//h1/text()").get().strip(" ")

        teacher = response.xpath("//td[contains(text(), 'Responsable')]/following::td[1]/text()").get().title()
        if 'Inconnu' in teacher:
            teachers = []
        elif ',' in teacher:
            teachers = [" ".join(teacher.split(", "))]
        else:
            teachers = [f"{teacher.split(' ')[1]} {teacher.split(' ')[0]}"]

        languages = response.xpath("//ul[li/h4[contains(text(), 'Langue')]]/li/text()").getall()
        languages = [l.strip(" \n") for l in languages]
        languages = [LANGUAGE_DICT[l] for l in languages if (l != '' and l != 'Aucun responsable ECTS')]
        languages = ['fr'] if len(languages) == 0 else languages

        content = cleanup(response.xpath(f"//ul[li/h4[contains(text(), 'Contenu')]]").get())
        content = content.replace("\n                    ", ' ')
        content = content.replace("Contenus          ", '')

        sections = ["Acquis", "Objectifs"]
        goals = []
        for section in sections:
            goals += [cleanup(response.xpath(f"//ul[li/h4[contains(text(), '{section}')]]").get())]
        goal = "\n".join(goals).strip("\n")
        goal = goal.replace("\n                    ", ' ')
        goal = goal.replace("Acquis d'apprentissage spécifiques sanctionnés par l'évaluation                         ",
                            "")
        goal = goal.replace("Objectifs          ", " ")

        yield {
            "id": ue_id,
            "name": ue_name,
            "year": f"{YEAR}-{YEAR+1}",
            "languages": languages,
            "teachers": teachers,
            "url": response.url,
            "content": content,
            "goal": goal,
            "activity": '',
            "other": ''
        }


