# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://helue.azurewebsites.net/ListingPub"


class HELProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole de la Ville de Liège
    """

    name = "hel-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}hel_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        faculties = response.xpath("//div[contains(@class, 'body-content')]/h3/text()").getall()
        for faculty in faculties:
            programs = response.xpath(f"//h3[text()=\"{faculty}\"]/following::div[1]/h3/text()").getall()
            for program in programs:
                courses_ids = response.xpath(f"//h3[text()=\"{program}\"]/following::div[1]//tr/td[1]/text()").getall()
                yield {"name": program,
                       "id": "",
                       "faculty": faculty,
                       "courses": [course_id.strip("\r\n ") for course_id in courses_ids]
                       }
