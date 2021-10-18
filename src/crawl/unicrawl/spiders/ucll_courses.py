# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URl = "https://onderwijsaanbod.limburg.ucll.be/syllabi/{}.htm"  # first format is code course, second is year
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}ucll_programs_{YEAR}.json')

LANGUAGES_DICT = {
    "Nederlands": 'nl',
    "Dutch": 'nl',
    "Olandese": 'nl',
    "Frans": 'fr',
    "French": 'fr',
    "Français": 'fr',
    "Engels": 'en',
    "English": 'en',
    "Deutsch": 'de',
    "Duits": 'de',
    "German": 'de',
    "Spanish": 'es',
    "Spaans": 'es',
    "Italiaans": 'it',
    "Chinees": 'cn'
}


class UCLLCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for UC Leuven-Limburg
    """

    # Warning https://onderwijsaanbod.limburg.ucll.be/syllabi/L/QD1610L.htm -> error 500

    name = "ucll-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ucll_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_urls = pd.read_json(open(PROG_DATA_PATH, "r"))["courses_urls"]
        courses_urls_list = sorted(list(set(courses_urls.sum())))

        for course_url in courses_urls_list:
            yield scrapy.Request(BASE_URl.format(course_url), self.parse_main)

    @staticmethod
    def parse_main(response):

        main_div = "//div[@id='hover_selectie_parent']"
        course_name = response.xpath(f"{main_div}//h2/text()").get()
        course_id = response.xpath(f"{main_div}//h2/span/text()").get().strip(')').split(" (B-UCLL-")[1]
        years = response.xpath("//div[@id='acjaar']/text()").get().strip("Academiejaar ").strip("Academic Year ")
        teachers = cleanup(response.xpath(f"{main_div}//span[contains(@class, 'Titularis') "
                                  f"or contains(@class, 'Coordinator')]").getall())
        teachers = [t.strip("\xa0|\xa0").replace("  (coordinator) ", '').replace("  (coördinator) ", '')
                    for t in teachers]
        teachers = list(set([t.strip(" ") for t in teachers if t != '']))

        languages = response.xpath(f"{main_div}//span[@class='taal']/text()").get()
        languages = [LANGUAGES_DICT[lang] for lang in languages.split(", ")] if languages is not None else []
        languages = ["nl"] if len(languages) == 0 else languages

        # Course description
        def get_sections_text(sections_names):
            texts = []
            for section in sections_names:
                texts += cleanup(response.xpath(f"//div[contains(@class, 'tab_content') "
                                                f"and h2/text()='{section}']//text()").getall())
            return "\n".join(texts).strip("\n")
        content = get_sections_text(['Content', 'Inhoud'])
        goal = get_sections_text(['Aims', 'Doelstellingen'])

        yield {
            'id': course_id,
            'name': course_name,
            'year': years,
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            'content': content,
            'goal': goal,
            'activity': '',
            'other': ''
        }
