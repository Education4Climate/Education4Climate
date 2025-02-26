# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER


BASE_URL = "https://paysage.henallux.be/ue-apercu/fr/{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}henallux_programs_{YEAR}.json')

LANGUAGE_DICT = {
    "français": "fr",
    "anglais": "en",
    "néerlandais": "nl",
    "allemand": "de"
}


class HENALLUXCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Haute Ecole de Namur-Liège-Luxembourg
    """

    name = "henallux-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}henallux_courses_{YEAR}_pre.json').as_uri()
    }

    def start_requests(self):

        courses_url_codes_ds = pd.read_json(open(PROG_DATA_PATH, "r"))["courses_url_codes"]
        courses_url_codes_list = sorted(list(set(courses_url_codes_ds.sum())))

        for course_code in courses_url_codes_list:
            yield scrapy.Request(url=BASE_URL.format(course_code), callback=self.parse_ue)

    @staticmethod
    def parse_ue(response):

        ue_id = cleanup(response.xpath("//div[@id='codeue']").get()).split(": ")[1]
        ue_name = response.xpath("//div[@class='intituleUE']/text()").get().strip(" \n")

        ue_div_txt = "//div[@class='identificationUE']"
        year = response.xpath(f"{ue_div_txt}//div[span[text()='Année académique']]/text()").get().split(": ")[1]

        language = response.xpath(f"{ue_div_txt}//div[span[text()=\"Langue d'enseignement\"]]/text()").get()
        languages = ['fr'] if language is None or language.strip(" \n\t") == ':' \
            else [LANGUAGE_DICT[language.split(": ")[1]]]

        teachers = response.xpath(f"{ue_div_txt}//div[span[text()=\"Responsable de l'UE\"]]/text()").get().split(": ")[1]
        teachers = teachers.split(", ")
        add_teachers = response.xpath(f"{ue_div_txt}//span[contains(text(), \"nseignants\")]/following::text()[1]").get().split(": ")[1]
        if add_teachers:
            teachers += add_teachers.split(", ")
        teachers = list(set([" ".join(teacher.split(" ")[1:]) + " " + teacher.split(" ")[0] for teacher in teachers]))
        teachers = [t.title() for t in teachers if t != " "]

        # Goals
        content = cleanup(response.xpath("//div[@id='section5']//p[text()='Contenus']/following::div[1]").get())
        goal = cleanup(response.xpath("//div[@id='section3']").get())\
            .replace("Acquis d’apprentissage spécifiques", '').strip(" \n")
        activity = cleanup(response.xpath("//div[@id='section6']").get())\
            .replace("Activité(s) d'apprentissage de cette UE", '').strip(" \n")

        yield {
            "id": ue_id,
            "name": ue_name,
            "year": year,
            "languages": languages,
            "teachers": teachers,
            "url": response.url,
            "content": content,
            "goal": goal,
            "activity": activity,
            "other": ''
        }
