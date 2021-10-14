# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URl = "http://progcours.vinci.be/cocoon/cours/{}.html"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}vinci_programs_{YEAR}.json')

LANGUAGES_DICT = {
    "Langue française": 'fr',
    "Langue anglaise": 'en'
}


class VINCICourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Haute Ecole Léonard de Vinci
    """

    name = "vinci-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}vinci_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        # Warning: COSV2430-1 leading to 500

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URl.format(course_id), self.parse_main, cb_kwargs={"course_id": course_id})

    @staticmethod
    def parse_main(response, course_id):

        course_name = response.xpath("////td[@class='LibCours']/text()").get()
        if course_name is None:
            yield {
                "id": course_id, "name": '', "year": f"{YEAR}-{int(YEAR) + 1}",
                "languages": ["fr"], "teachers": [], "url": response.url,
                "content": '', "goal": '', "activity": '', "other": ''
            }
        years = response.xpath("//div[@id='TitrePrinc']/text()").get().split(" ")[-1]
        course_rubric_txt = "//div[@class='TitreRubCours' and contains(text(), \"{}\")]"

        teachers = cleanup(response.xpath(f"{course_rubric_txt.format('prof')}/following::tr[1]//a").getall())
        teachers += cleanup(response.xpath(f"{course_rubric_txt.format('Coord')}/following::tr[1]//a").getall())
        teachers = [t.replace(" ", '') for t in teachers]
        teachers = list(set(teachers))
        teachers = [" ".join(teacher.split(" ")[1:]).lower().title() + " " + teacher.split(" ")[0].strip(" ")
                    for teacher in teachers]

        languages = response.xpath(course_rubric_txt.format("Langue(s)") + "/following::td[2]/text()").getall()
        languages = [LANGUAGES_DICT[l] for l in languages]
        languages = ["fr"] if len(languages) == 0 else languages

        # Cours description
        def get_sections_text(section_name_prec, section_name_follow):
            texts = cleanup(response.xpath(f"//tr[preceding::tr[@id='rub_{section_name_prec}'] "
                                           f"and following::tr[@id='rub_{section_name_follow}']]").getall())
            return '\n'.join(texts).strip("\n")
        content = get_sections_text('APER', 'OBJT')
        goal = get_sections_text('OBJT', 'PRER')
        activity = get_sections_text('TRPR', 'ORGA')

        yield {
            'id': course_id,
            'name': course_name,
            'year': years,
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            "content": content,
            "goal": goal,
            "activity": activity,
            "other": ''
        }
