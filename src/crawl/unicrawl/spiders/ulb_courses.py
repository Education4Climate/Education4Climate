from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'https://www.ulb.be/fr/programme/{}'  # TODO: some work with '-1' at the end
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}ulb_programs_{YEAR}.json')

LANGUAGE_DICT = {
    "français": "fr",
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
    "Croate": "hr"
}


class ULBCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Université Libre de Bruxelles
    """

    name = 'ulb-courses'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ulb_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(
                url=BASE_URL.format(course_id.lower()),
                callback=self.parse_course,
                cb_kwargs={'course_id': course_id}
            )

    @staticmethod
    def parse_course(response, course_id):

        name = response.xpath("//h1/text()").get()
        if name is None:
            yield {
                "id": course_id, "name": '', "year": f'{YEAR}-{int(YEAR) + 1}',
                "languages": [], "teachers": [], "url": response.url,
                "content": '', "goal": '', "activity": '', "other": ''
            }
            return
        name = name.replace("\n               ", '')

        teachers = cleanup(response.xpath("//h3[text()='Titulaire(s) du cours']/following::text()[1]").get())
        teachers = teachers.replace(" (Coordonnateur)", "").replace(" et ", ", ").replace("\n               ", '')
        teachers = teachers.split(", ")
        teachers = [teacher.title() for teacher in teachers if teacher != ""]
        # Put surname first
        teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]

        languages = response.xpath("//h3[text()=\"Langue(s) d'enseignement\"]/following::p[1]/text()").get()
        if languages is not None:
            languages = [LANGUAGE_DICT[language] if language in LANGUAGE_DICT else 'other'
                         for language in languages.split(", ")]
        languages = ['fr'] if languages is None or languages == [""] or len(languages) == 0 else languages

        # Course description
        def get_sections_text(sections_names):
            texts = [cleanup(response.xpath(f"//h2[text()=\"{section}\"]/following::div[1]").get())
                     for section in sections_names]
            return "\n".join(texts).strip("\n ")
        content = get_sections_text(["Contenu du cours"])
        goal = get_sections_text(["Objectifs (et/ou acquis d'apprentissages spécifiques)"])
        activity = get_sections_text(["Méthodes d'enseignement et activités d'apprentissages"])

        yield {
            "id": course_id,
            "name": name,
            "year": f'{YEAR}-{int(YEAR) + 1}',
            "languages": languages,
            "teachers": teachers,
            "url": response.url,
            "content": content,
            "goal": goal,
            "activity": activity,
            "other": ''
        }
