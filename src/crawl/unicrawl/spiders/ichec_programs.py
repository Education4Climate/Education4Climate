# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.ichec.be/fr/programmes"
CAMPUS_MAPPING = {
    "bac": ["Anjou", "Montgomery"],
    "master": ["Anjou"],
    "other": ["Montgomery"]
}  # campus is deduced, not crawled


class ICHECProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for ICHEC Brussel Management School
    """

    name = "ichec-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ichec_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        links = response.css(".formation-link a")
        yield from response.follow_all(links, self.parse_program)

    @staticmethod
    def parse_program(response):

        horaire = "soir" if ("soir" in response.url) else ""  # distinguish day and night versions of programs
        program_name = response.xpath("//div[@class='formation-title']//h1/text()").get().replace("  ", " ").strip()
        program_name = "{} - {}".format(program_name, horaire) if horaire else program_name

        # no id it seems - make it up by taking first letter of each word
        program_id = "".join([keyword[0].upper() for keyword in program_name.split(" ")
                              if keyword is not None and keyword not in [':', ',', '(', '-']])

        cycle = response.xpath("//div[@class='formation-banner-info-item'][1]/text()[2]").get().strip(" \n").lower()
        if 'bac' in cycle:
            cycle = 'bac'
        elif cycle == 'master':
            cycle = 'master'
        else:
            cycle = 'other'

        # Anjou from bac2 to master2, Montgomery for the rest (see https://www.ichec.be/fr/nos-campus)
        campuses = CAMPUS_MAPPING[cycle]

        ue_ids = response.css(".modal-link::text").getall()
        ue_ects = response.xpath("//div[@class='formation-tab-content structure']//table//td[5]/text()").getall()
        ue_ects = [int(e) for e in ue_ects]

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculties": ["Ecole de gestion et commerce"],  # no explicit faculty
            "campuses": campuses,
            "url": response.url,
            "courses": ue_ids,
            "ects": ue_ects,
        }
