# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR
import pandas as pd

BASE_URL = "https://fiches-ue.icampusferrer.eu/locked_list.php"


class HEFERRERProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole Francisco Ferrer
    """

    name = "he-ferrer-programs"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/he-ferrer_programs_{YEAR}.json',
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

