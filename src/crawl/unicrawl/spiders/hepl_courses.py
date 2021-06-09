# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = "https://ecolevirtuelle.provincedeliege.be/docStatique/ects/{}" + f"-{YEAR}.html"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}hepl_programs_{YEAR}.json')

LANGUAGE_DICT = {"Français": "fr",
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

        ue_name = response.xpath("//h4[contains(text(), 'Information')]/text()").get().split(": ")[1].strip('" ')

        campus = response.xpath("//td[text()='Implantation(s)']/following::td[1]/text()").get().split(" - ")[1]

        teacher = response.xpath("//td[contains(text(), 'Responsable')]/following::td[1]/text()").get()
        teachers = [" ".join(teacher.split(", "))]

        languages = response.xpath("//ul[li/h4[contains(text(), 'Langue')]]/li/text()").getall()
        languages = [l.strip(" \n") for l in languages]
        languages = [LANGUAGE_DICT[l] for l in languages if (l != '' and l != 'Aucun responsable ECTS')]

        sections = ["Acquis", "Objectifs", "Contenus"]
        contents = []
        for section in sections:
            contents += [cleanup(response.xpath(f"//ul[li/h4[contains(text(), '{section}')]]").get())]
        content = "\n".join(contents)
        content = "" if content == "\n\n" else content
        content = content.replace("\n                    ", ' ')

        yield {
            "id": ue_id,
            "name": ue_name,
            "year": f"{YEAR}-{YEAR+1}",
            "languages": languages,
            "teachers": teachers,
            "campus": campus,
            "url": response.url,
            "content": content
        }


