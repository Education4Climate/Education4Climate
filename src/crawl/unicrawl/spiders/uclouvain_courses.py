# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import numpy as np
import pandas as pd

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = "https://uclouvain.be/cours-{}-{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}uclouvain_programs_{YEAR}.json')


LANGUAGE_DICT = {
    "Français": "fr",
    "Anglais": "en",
    "Allemand": "de",
    "Neerlandais": "nl",
    "Italien": "it",
    "Espagnol": "es",
    "Portugais": "pt",
    "Arabe": 'ar',
    "Grec": "gr",
    "Japonais": 'jp',
    "Russe": "ru"
}


class UCLouvainCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Université Catholique de Louvain
    """

    name = "uclouvain-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}uclouvain_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_list = sorted(list(set(courses.sum())))

        for course_id in courses_list:
            yield scrapy.Request(url=BASE_URL.format(YEAR, course_id),
                                 callback=self.parse_course,
                                 cb_kwargs={"course_id": course_id})

    @staticmethod
    def parse_course(response, course_id):

        course_name = cleanup(response.css("h1.header-school::text").get())
        year = cleanup(response.css("span.anacs::text").get())

        teachers = response.xpath("//div[div[contains(text(),'Enseignants')]]/div/a/text()").getall()
        languages = cleanup(response.xpath("//div[div[contains(@class, 'fa_cell_1') and contains(text(), 'Langue')]]"
                                           "/div[2]/text()").getall())
        languages = [LANGUAGE_DICT[l] if l in LANGUAGE_DICT else 'fr' for l in languages]
        languages = ["fr"] if len(languages) == 0 else languages
        languages = list(np.unique(languages))

        # Course description
        def get_section(section):

            xpaths={
                    'Contenu':"//div[contains(text(),'Contenu') and @class='col-sm-2 fa_cell_1']/following-sibling::div/text()",
                    'Thèmes': "//div[contains(text(),'Thèmes' ) and @class='col-sm-2 fa_cell_1']/following-sibling::div/text()",
                    'Acquis': "//div[contains(text(),'Acquis' ) and @class='col-sm-2 fa_cell_1']/following-sibling::div/descendant::td/text()"
                   }

            txt = cleanup(response.xpath(xpaths[section]).getall())

            return "\n".join(txt).strip("\n ")

        content = get_section('Contenu')
        goal = get_section('Acquis')
        themes = get_section('Thèmes')

        yield {
            'id': course_id,
            'name': course_name,
            'year': year,
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            'content': content,
            'goal': goal,
            'activity': '',
            'other': themes
        }
