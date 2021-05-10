# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://fiches-ue.icampusferrer.eu/locked_list.php"


class HEFERRERProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole Francisco Ferrer
    """

    name = "he-ferrer-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}he-ferrer_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    @staticmethod
    def parse_main(response):
        ue_names = response.xpath("//tr//td[3]/text()").getall()
        programs = response.xpath("//tr//td[4]/text()").getall()
        df = pd.DataFrame({'ue': ue_names, 'program': programs})
        for program in sorted(list(set(programs))):
            yield {"name": program,
                   "id": "",
                   "courses": df[df["program"] == program]['ue'].to_list()}

