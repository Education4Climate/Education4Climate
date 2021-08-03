from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

# PATH_COURS_URL = urllib.parse.quote(
#    '/ws/ksup/course-programmes?anac={}&mnemonic={}&lang=fr',
#    safe='{}'
# )
# COURS_URL = f'https://www.ulb.be/api/formation?path={PATH_COURS_URL}'
BASE_URL = 'https://www.ulb.be/fr/programme/'
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}ulb_programs_{YEAR}.json')

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
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ulb_courses_{YEAR}.json').as_uri()
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

        name = response.xpath("//h1/text()").get()
        if name is None:
            return
        name = name.replace("\n               ", '')

        teachers = cleanup(response.xpath("//h3[text()='Titulaire(s) du cours']/following::text()[1]").get())
        teachers = teachers.replace(" (Coordonnateur)", "").replace(" et ", ", ").replace("\n               ", '')
        teachers = teachers.split(", ")
        teachers = [teacher for teacher in teachers if teacher != ""]
        # Put surname first
        teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]

        languages = response.xpath("//h3[text()=\"Langue(s) d'enseignement\"]/following::p[1]/text()").get()
        if languages is not None:
            languages = [LANGUAGE_DICT[language] for language in languages.split(", ")]
        languages = ['fr'] if languages == [""] else languages

        # TODO: update
        content_titles = ["Contenu du cours", "Objectifs (et/ou acquis d'apprentissages spécifiques)",
                          "Méthodes d'enseignement et activités d'apprentissages"]
        content = "\n".join([cleanup(response.xpath(f"//h2[text()=\"{title}\"]/following::div[1]").get())
                             for title in content_titles]).strip("\n ")

        cur_dict = {
            "name": name,
            "teachers": teachers,
            "year": f'{YEAR}-{int(YEAR) + 1}',
            "languages": languages,
            "url": response.url,
            "content": content
        }

        yield {**base_dict, **cur_dict}
