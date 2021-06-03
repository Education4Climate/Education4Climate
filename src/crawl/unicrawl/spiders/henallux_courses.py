# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER


BASE_URL = "https://paysage.henallux.be/cursus/infoue/idUe/{}/idCursus/{}/anacad/{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}henallux_programs_{YEAR}.json')
LANGUAGE_DICT = {"F": "fr",
                 "A": "en",
                 "N": "nl"}


class HENALLUXCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for Haute Ecole de Namur-Liège-Luxembourg
    """

    name = "henallux-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}henallux_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        courses_url_codes_ds = pd.read_json(open(PROG_DATA_PATH, "r"))["courses_url_codes"]

        for program_id in courses_url_codes_ds.index:
            courses_codes = courses_url_codes_ds.loc[program_id]
            for course_code in courses_codes:
                yield scrapy.Request(url=BASE_URL.format(course_code, program_id, YEAR),
                                     callback=self.parse_ue)

    @staticmethod
    def parse_ue(response):

        ue_id = response.xpath("//span[@class='important']/text()").get()
        ue_name = response.xpath("//div[@class='intituleUE']/span/text()").get()
        ue_div_txt = "//div[@class='identificationUE']"
        year = response.xpath(f"{ue_div_txt}//div[span[text()='Année académique']]/text()").get().split(": ")[1]
        languages = response.xpath(f"{ue_div_txt}//div[span[text()=\"Langue d'enseignement\"]]/text()").get().split(": ")[1]
        languages = [LANGUAGE_DICT[language] for language in languages]
        teachers = response.xpath(f"{ue_div_txt}//div[span[text()=\"Responsable de l'UE\"]]/text()").get().split(": ")[1]
        teachers = teachers.split(" - ")
        add_teachers = response.xpath(f"{ue_div_txt}//span[contains(text(), \"Autres enseignants\")]/following::text()[2]").get()
        if add_teachers is not None:
            teachers += add_teachers.split(" - ")
        teachers = list(set([" ".join(teacher.split(" ")[1:]) + " " + teacher.split(" ")[0] for teacher in teachers]))
        teachers = [t for t in teachers if t != " "]

        sections = ['Acquis', 'Contenu']
        contents = []
        for section in sections:
            contents += [cleanup(response.xpath(f"//div[contains(text(), \"{section}\")]/following::div[1]").get())]
        content = "\n".join(contents).strip("\n")

        yield {"id": ue_id,
               "name": ue_name,
               "year": year,
               "teachers": teachers,
               "languages": languages,
               "url": response.url,
               "content": content
               }
