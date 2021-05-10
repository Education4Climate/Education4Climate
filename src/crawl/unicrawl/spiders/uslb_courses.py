# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}uslb_programs_{YEAR}.json')
BASE_URL = "https://www.usaintlouis.be/sl/2020/C{}.html"
LANGUAGE_DICT = {"français": 'fr',
                 "francais": 'fr',
                 "french": 'fr',
                 "anglais": 'en',
                 "english": 'en',
                 "allemand": 'de',
                 "espagnol": 'es',
                 "italien": 'it',
                 "néerlandais": 'nl',
                 "nederlands": 'nl',
                 "dutch": 'nl'}


class USLBCoursesSpider(scrapy.Spider, ABC):
    name = "uslb-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}uslb_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        courses_codes = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_codes_list = sorted(list(set(courses_codes.sum())))

        for course_code in courses_codes_list:
            # Some codes have a additional letter in their code not used in the url
            base_dict = {"id": course_code}
            course_code = course_code[1:] if len(course_code) != 8 else course_code
            yield scrapy.Request(url=BASE_URL.format(course_code), callback=self.parse_course,
                                 cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_course(response, base_dict):

        title = response.css('p.ProgrammeTitre::text').get().strip()
        course_name = title.split(' - ')[1]

        teachers = response.xpath("//div[contains(@class, 'prof')]//a/text()").getall()
        language_description = response.xpath("//div/b[text()=\"Langues d'enseignement\"]/following::div[1]/text()").get()
        language_description = language_description.strip("\r ")
        languages_codes = []
        for lang, code in LANGUAGE_DICT.items():
            if lang in language_description.lower():
                languages_codes += [code]
        languages_codes = list(set(languages_codes))

        sections = ["Objectifs d'apprentissage", "Contenu de l'activité"]
        content = ''
        for section in sections:
            section_content = cleanup(response.xpath(f"//div/b[text()=\"{section}\"]/following::div[1]").get())
            content += "\n" + section_content if len(section_content) != 0 else ''
        content = content.strip("\n")
        content = "" if content == "/\n/" else content

        cur_dict = {"name": course_name,
                    "languages": languages_codes,
                    "teachers": teachers,
                    "year": f"{YEAR}-{int(YEAR)+1}",
                    "url": response.url,
                    "content": content}
        yield {**base_dict, **cur_dict}
