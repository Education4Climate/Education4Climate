# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

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
        languages = [LANGUAGE_DICT[l] if l in LANGUAGE_DICT else 'other' for l in languages]
        
        # Course description
        def get_sections_text(sections_names):
            texts = [cleanup(response.xpath(f"//div[div[contains(text(),'{section}')]]/div[2]").get())
                     for section in sections_names]
            return "\n".join(texts).strip("\n ")
        content = get_sections_text(['Contenu'])
        goal = get_sections_text(['Acquis'])
        themes = get_sections_text(['Thèmes'])

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
