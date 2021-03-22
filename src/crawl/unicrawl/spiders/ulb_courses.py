from abc import ABC
from pathlib import Path
import urllib.parse

import pandas as pd

import scrapy

from config.settings import YEAR
from config.utils import cleanup

# PATH_COURS_URL = urllib.parse.quote(
#    '/ws/ksup/course-programmes?anac={}&mnemonic={}&lang=fr',
#    safe='{}'
# )
# COURS_URL = f'https://www.ulb.be/api/formation?path={PATH_COURS_URL}'
BASE_URL = 'https://www.ulb.be/fr/programme/'
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../data/crawling-output/ulb_programs_{YEAR}.json')

LANGUAGE_DICT = {"français": "fr",
                 "anglais": "en",
                 "Inconnu": "",
                 "Néerlandais": "nl",
                 "Allemand": "de",
                 "Chinois": "cn",
                 "Arabe": "ar",
                 "Russe": "ru",
                 "Italien": "it",
                 "Espagnol": "es",
                 "Grec moderne": "gr",
                 "Japonais": "jp",
                 "Turc": "tr",
                 "Persan": "fa",
                 "Roumain": "ro",
                 "Portugais": "pt",
                 "Polonais": "pl",
                 "Tchèque": "cz",
                 "Slovène": "si",
                 "Croate": "hr"}


class ULBCourseSpider(scrapy.Spider, ABC):
    name = 'ulb-courses'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../data/crawling-output/ulb_courses_{YEAR}.json')
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum()))) 

        for course_id in courses_ids_list:
            base_dict = {'id': course_id}

            yield scrapy.Request(
                url=f'{BASE_URL}{course_id.lower()}',
                callback=self.parse_course,
                cb_kwargs={'base_dict': base_dict}
            )

    @staticmethod
    def parse_course(response, base_dict):

        name = response.xpath("//h1/text()").get()x
        teachers = cleanup(response.xpath("//h3[text()='Titulaire(s) du cours']/following::text()[1]").get())
        teachers = teachers.replace(" (Coordonnateur)", "").replace(" et ", ", ")
        teachers = teachers.split(", ")

        # TODO: move that into the program code
        ects = response.xpath("//h3[text()='Crédits ECTS']/following::p[1]/text()").get()
        ects = int(ects) if 1 <= len(ects) <= 2 else None

        # TODO: check if there can be multiple languages
        languages = response.xpath("//h3[text()=\"Langue(s) d'enseignement\"]/following::p[1]/text()").get()
        if languages is not None:
            languages = [LANGUAGE_DICT[language] for language in languages.split(", ")]
        languages = [] if languages == [""] else languages

        content_titles = ["Contenu du cours", "Objectifs (et/ou acquis d'apprentissages spécifiques)",
                          "Méthodes d'enseignement et activités d'apprentissages"]
        content = "\n".join([cleanup(response.xpath(f"//h2[text()=\"{title}\"]/following::div[1]").get())
                             for title in content_titles])
        content = "" if content == "\n\n" else content

        cur_dict = {
            "name": name,
            "teachers": teachers,
            "year": f'{YEAR}-{int(YEAR) + 1}',
            "languages": languages,
            "url": response.url,
            "content": content
        }

        yield {**base_dict, **cur_dict}
