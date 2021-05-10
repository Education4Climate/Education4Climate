# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URl = "http://onderwijsaanbod.kuleuven.be/syllabi/{}.htm"  # first format is code course, second is year
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}kuleuven_programs_{YEAR}.json')

LANGUAGES_DICT = {"Nederlands": 'nl',
                  "Dutch": 'nl',
                  "Frans": 'fr',
                  "French": 'fr',
                  "Français": 'fr',
                  "Engels": 'en',
                  "English": 'en',
                  "Deutsch": 'de',
                  "German": 'de',
                  "Duits": 'de',
                  "Spanish": 'es',
                  "Spaans": 'es',
                  "Español": 'es',
                  "Italian": 'it',
                  "Italiaans": 'it',
                  "Italiano": 'it',
                  "Polish": 'pl',
                  "Pools": 'pl',
                  "Russisch": 'ru',
                  "Arabic": 'ar',
                  "Arabisch": 'ar',
                  "Japans": 'jp',
                  "Chinees": 'cn',
                  'Korean': 'kr'}


class KULeuvenCourseSpider(scrapy.Spider, ABC):
    name = "kuleuven-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}kuleuven_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_urls = pd.read_json(open(PROG_DATA_PATH, "r"))["courses_urls"]
        courses_urls_list = sorted(list(set(courses_urls.sum())))

        print(len(courses_urls_list))
        for course_url in courses_urls_list:
            yield scrapy.Request(BASE_URl.format(course_url), self.parse_main)

    @staticmethod
    def parse_main(response):
        main_div = "//div[@id='hover_selectie_parent']"
        course_name = response.xpath(f"{main_div}//h2/text()").get()
        course_id = response.xpath(f"{main_div}//h2/span/text()").get().strip(')').split(" (B-KUL-")[1]
        years = response.xpath("//div[@id='acjaar']/text()").get().strip("Academiejaar ").strip("Academic Year ")
        teachers = response.xpath(f"{main_div}//span[contains(@class, 'Titularis') "
                                  f"or contains(@class, 'Coordinator')]//a/text()").getall()
        teachers = [t.strip("\xa0|\xa0") for t in teachers]
        teachers = list(set([t for t in teachers if t != '']))
        languages = response.xpath(f"{main_div}//span[@class='taal']/text()").get()
        languages = [LANGUAGES_DICT[lang] for lang in languages.split(", ")] if languages is not None else []

        # Content
        content = []
        sections = ['Aims', 'Doelstellingen', 'Content', 'Inhoud']
        for section in sections:
            content += cleanup(response.xpath(f"//div[contains(@class, 'tab_content') "
                                              f"and h2/text()='{section}']//text()").getall())

        content = " ".join(content)

        yield {
            'id': course_id,
            'name': course_name,
            'year': years,
            'teachers': teachers,
            'languages': languages,
            'content': content,
            'url': response.url
        }
