# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = f"https://webcontent.umons.ac.be/web/fr/pde/{YEAR}-{int(YEAR)+1}" + "/ue/{}.htm"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}umons_programs_{YEAR}.json')

LANGUAGE_DICT = {
    "Français": "fr",
    "Anglais": "en",
    "Néerlandais": "nl",
    "Allemand": "de",
    "Espagnol": "es",
    "Danois": "dk",
    "Italien": "it",
    "Russe": "ru",
    "Arabe": "ar",
    "Chinois": "cn",
    "Japonais": "jp",
    "Norvégien": "no",
    "Polonais": "po",
    "Portugais": "pt",
    "Suédois": "se",
    "Grec": "gr"
}


class UmonsCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for University of Mons
    """

    name = "umons-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}umons_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_list = sorted(list(set(courses.sum())))

        for course_id in courses_list:
            yield scrapy.Request(url=BASE_URL.format(course_id),
                                 callback=self.parse_course,
                                 cb_kwargs={"course_id": course_id})

    @staticmethod
    def parse_course(response, course_id):

        course_name = response.css("td.UETitle::text").get()
        if not course_name:
            yield {'id': course_id, 'name': '', 'year':  f"{YEAR}-{YEAR+1}",
                   'languages': [], 'teachers': [], 'url': response.url,
                   'content': '', 'goal': '', 'activity': '', 'other': ''}
            return

        year = response.css('td.toptile::text').get().split(' ')[2]

        main_teacher = response.xpath("//table[@class='UETbl'][1]//td[3]//text()").get()
        teachers = list(set([main_teacher] + response.xpath("//table[@class='UETbl'][1]//td[5]//li/text()").getall()))
        teachers = [teacher.title() for teacher in teachers if 'N.' not in teacher]

        languages = response.xpath("//table[@class='UETbl'][2]//td[1]//li/text()").getall()
        languages_codes = []
        for languages_list in languages:
            languages_codes += \
                [LANGUAGE_DICT[l.replace(" niveau 1", '').replace(" niveau 2", '').replace(" niveau 3", '')]
                 for l in languages_list.split(', ')]
        languages_codes = ["fr"] if len(languages_codes) == 0 else languages_codes

        # Course description
        def get_sections_text(sections_names):
            texts = [cleanup(response.xpath(f"//div[p[contains(text(), \"{section}\")]]/p[@class='texteRubrique']").get())
                     for section in sections_names]
            return "\n".join(texts).strip("\n ")
        content = get_sections_text(["Contenu de l'UE"])
        goal = get_sections_text(["Acquis d'apprentissage"]) #  + "\n" \
        # + cleanup(response.xpath(f"//div[p/text()="
        #                          f"\"Objectifs par rapport aux acquis d'apprentissage du programme\"]/ul").get())
        goal = goal.strip("\n")

        yield {
            'id': course_id,
            'name': course_name,
            'year': year,
            'languages': languages_codes,
            'teachers': teachers,
            'url': response.url,
            'content': content,
            'goal': goal,
            'activity': '',
            'other': ''
        }
