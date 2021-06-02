# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://fiches-ue.icampusferrer.eu/locked_list.php"
FACULTIES_AND_CAMPUS = {"AA": ['Arts Appliqués', "Site Palais du Midi"],
                        "Eco": ['Economique', 'Site Anneessens'],
                        "ParaMed": ['Paramédical', 'Site Brugmann'],
                        "Peda": ['Pédagogique', 'Site Lemonnier'],
                        "Soc": ['Social', 'Site Anneessens'],
                        "Tech": ['Technique', 'Site Palais du Midi']}
PROGRAMS_FACULTIES_AND_CAMPUS = {"Arts du tissu": []}


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
        ue_links = response.xpath("//tr//td[1]/a/@href").getall()
        print("aie")
        print(ue_links)
        programs = response.xpath("//tr//td[4]/text()").getall()
        df = pd.DataFrame({'ue': ue_names, 'program': programs})
        for i, program in enumerate(sorted(list(set(programs)))):
            print(program)
            yield {"id": i,
                   "name": program,
                   "courses": df[df["program"] == program]['ue'].to_list()}

