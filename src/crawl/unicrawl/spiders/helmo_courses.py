# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from config.utils import cleanup
from config.settings import YEAR

BASE_URl = "https://www.helmo.be/Formations/{}"
PROG_DATA_PATH = Path(f'../../data/crawling-output/helmo_programs_{YEAR}.json')

LANGUAGES_DICT = {"Français": 'fr',
                  "Anglais": 'en'}


class HELMOCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for Haute Ecole Libre Mosane
    """

    name = "helmo-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/helmo_courses_{YEAR}.json',
    }

    def start_requests(self):

        courses_df = pd.read_json(open(PROG_DATA_PATH, "r"))[["courses", "courses_urls"]]
        courses_ids_list = courses_df["courses"].sum()
        courses_urls_list = courses_df["courses_urls"].sum()
        courses_ids_urls = sorted(list(set(zip(courses_ids_list, courses_urls_list))))

        for course_id, course_url in courses_ids_urls:
            base_dict = {"id": course_id}
            yield scrapy.Request(BASE_URl.format(course_url), self.parse_main, cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_main(response, base_dict):

        ue_name = cleanup(response.xpath("//section[@id='helmoContent']//h3/text()").get())
        # TODO: check if there cannot be more than one main teacher
        main_teacher = response.xpath("//div[text()=\"Responsable de l'UE :\"]/following::span[1]/text()").get()
        sub_teachers = response.xpath("//div[text()=\"Autres intervenants :\"]/following::span[1]/text()").get()
        teachers = [main_teacher]
        if sub_teachers is not None:
            teachers += sub_teachers.split(",")

        years = response.xpath("//div[text()=\"Année académique :\"]/following::span[1]/text()").get()

        languages = response.xpath("//div[text()=\"Langue d'enseignement :\"]/following::span[1]/text()").get()
        languages = [LANGUAGES_DICT[languages]]

        sections = ["Objectifs", "Acquis", "Contenu", "Dispositif"]
        contents = [cleanup(response.xpath(f"//h4[contains(text(), \"{section}\")]/following::div[1]").get())
                    for section in sections]
        content = "\n".join(contents)
        content = "" if content == "\n\n" else content

        cur_dict = {
            'name': ue_name,
            'year': years,
            'teacher': teachers,
            'language': languages,
            'url': response.url,
            'content': content
        }
        yield {**base_dict, **cur_dict}
