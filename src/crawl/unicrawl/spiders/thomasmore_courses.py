# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from config.settings import YEAR
from config.utils import cleanup

BASE_URl = "http://onderwijsaanbodmechelenantwerpen.thomasmore.be/syllabi/{}.htm"  # first format is code course, second is year
PROG_DATA_PATH = Path(f'../../data/crawling-output/thomasmore_programs_{YEAR}.json')

# TODO: check languages
LANGUAGES_DICT = {"Nederlands": 'nl',
                  "Dutch": 'nl',
                  "Frans": 'fr',
                  "French": 'fr',
                  "Engels": 'en',
                  "English": 'en',
                  "Deutsch": 'de',
                  "Duits": 'de'}


class ThomasMoreCourseSpider(scrapy.Spider, ABC):
    name = "thomasmore-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/thomasmore_courses_{YEAR}.json',
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
        course_id = response.xpath(f"{main_div}//h2/span/text()").get().strip(')').split(" (B-TM-")[1]
        years = response.xpath("//div[@id='acjaar']/text()").get().strip("Academiejaar ").strip("Academic Year ")
        teachers = response.xpath(f"{main_div}//span[contains(@class, 'Titularis')]//text()").getall()
        teachers = [t.strip("\xa0|\xa0") for t in teachers]
        teachers = [t for t in teachers if t != '']
        languages = response.xpath(f"{main_div}//span[@class='taal']/text()").getall()
        languages = [LANGUAGES_DICT[lang] for lang in languages]

        # TODO: maybe a bit barbaric
        content = cleanup(response.xpath("//div[contains(@class, 'tab_content')]//text()").getall())
        content = " ".join(content)

        yield {
            'name': course_name,
            'id': course_id,
            'year': years,
            'teacher': teachers,
            'language': languages,
            'content': content,
            'url': response.url,
        }
