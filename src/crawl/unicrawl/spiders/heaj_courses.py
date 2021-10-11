# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URl = "http://progcours.heaj.be/cocoon/cours/{}.html"  # first format is code course, second is year
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}heaj_programs_{YEAR}.json')

LANGUAGES_DICT = {"Langue française": 'fr',
                  "Langue anglaise": 'en',
                  "Langue néerlandaise": 'nl',
                  "Langue italienne": 'it',
                  "Langue espagnole": 'es',
                  "Langue allemande": 'de'}


class HECHCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for Haute Ecole Albert Jacquard
    """

    name = "heaj-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}heaj_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URl.format(course_id), self.parse_main, cb_kwargs={"course_id": course_id})

    @staticmethod
    def parse_main(response, course_id):

        course_name = response.xpath("////td[@class='LibCours']/text()").get()
        if course_name is None:
            return
        years = response.xpath("//div[@id='TitrePrinc']/text()").get().split(" ")[-1]
        course_rubric_txt = "//div[@class='TitreRubCours' and contains(text(), \"{}\")]"

        teachers = cleanup(response.xpath(f"{course_rubric_txt.format('prof')}/following::tr[1]//a").getall())
        teachers += cleanup(response.xpath(f"{course_rubric_txt.format('Coord')}/following::tr[1]//a").getall())
        teachers = [t.replace(" ", '') for t in teachers]
        teachers = list(set(teachers))
        teachers = [" ".join(teacher.split(" ")[1:]) + " " + teacher.split(" ")[0].strip(" ")
                    for teacher in teachers]

        languages = response.xpath(course_rubric_txt.format("Langue(s)") + "/following::td[2]/text()").getall()
        languages = [LANGUAGES_DICT[l] for l in languages]

        contents = cleanup(response.xpath("//tr[preceding::tr[@id='rub_APER'] "
                                          "and following::tr[@id='rub_OBJT']]").getall())
        contents += cleanup(response.xpath("//tr[preceding::tr[@id='rub_OBJT']"
                                           " and following::tr[@id='rub_PRER']]").getall())
        content = '\n'.join(contents)
        content = '' if content == '\n' else content

        yield {
            'id': course_id,
            'name': course_name,
            'year': years,
            'teachers': teachers,
            'languages': languages,
            'url': response.url,
            'content': content
        }
