# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = f"http://p4580.phpnet.org/{YEAR}-{YEAR+1}/"


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

    @staticmethod
    def parse_main(response):

        faculties = response.xpath("//div[contains(@class, 'body-content')]/h3/text()").getall()
        for i, faculty in enumerate(faculties):

            programs = response.xpath(f"//h3[text()=\"{faculty}\"]/following::div[1]/h3/text()").getall()
            for j, program in enumerate(programs):

                ue_ids = response.xpath(f"//h3[text()=\"{program}\"]/following::div[1]//tr/td[1]/text()").getall()
                ue_ids = [ue_id.strip("\r\n ") for ue_id in ue_ids]
                ue_urls = response.xpath(f"//h3[text()=\"{program}\"]/following::div[1]//tr//a/@href").getall()
                ue_urls_ids = [link.split("/")[-1].strip(".html") for link in ue_urls]

                yield {
                    "id": f"{i}-{j}",
                    "name": program,
                    "cycle": 'bac',
                    "faculty": faculty,
                    "url": response.url,
                    "courses": ue_ids,
                    "ue_urls_ids": ue_urls_ids
                }
