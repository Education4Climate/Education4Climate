# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.helmo.be/fr/formations/{}/{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}helmo_programs_{YEAR}.json')

LANGUAGES_DICT = {
    "Français": 'fr',
    "Anglais": 'en',
    "Allemand": 'de'
}


class HELMOCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Haute Ecole Libre Mosane
    """

    name = "helmo-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}helmo_courses_{YEAR}_pre.json').as_uri()
    }

    def start_requests(self):

        courses_df = pd.read_json(open(PROG_DATA_PATH, "r"))[["id_url", "courses"]].set_index('id_url')

        for program_id_url, courses in courses_df['courses'].items():
            for course_id in courses:
                yield scrapy.Request(BASE_URL.format(program_id_url, course_id), self.parse_main, cb_kwargs={"ue_id": str(course_id)})

    @staticmethod
    def parse_main(response, ue_id):

        ue_name = response.xpath("//h1/text()").get()

        teachers = cleanup(response.xpath("//li[h4[text()='Responsable de cette UE']]//div/text()").getall())
        teachers += response.xpath("//li[h4[text()='Enseignants prenant part à cette UE']]//div/a/text()").getall()
        teachers = [t.strip(" ").title() for t in teachers]

        years = f"{YEAR}-{YEAR-2000+1}"

        languages = cleanup(response.xpath("//li[h4[contains(text(), 'Langue')]]//div/text()").get())
        languages = [LANGUAGES_DICT[languages]]

        content = cleanup(response.xpath("//h4[contains(text(), 'contenus')]"
                                         "//following-sibling::*[following::h4[contains(text(), 'acquis')]]").getall())
        content = '\n'.join(content).strip("\n")

        goal = cleanup(response.xpath("//div[h4[contains(text(), 'acquis')]]"
                                      "/*[preceding::h4[contains(text(), 'acquis')]]").getall())
        goal = '\n'.join(goal).strip("\n")

        yield {
            'id': ue_id,
            'name': ue_name,
            'year': years,
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            'content': content,
            'goal': goal,
            'activity': '',
            'other': ''
        }
