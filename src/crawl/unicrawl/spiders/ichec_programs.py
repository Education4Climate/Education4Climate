# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.ichec.be/fr/programmes"
CAMPUS_MAPPING = {"bachelier": "Anjou, Montgomery", "master": "Anjou", "other": "Montgomery"} # campus is deduced, not crawled


class ICHECProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for ICHEC Brussel Management School
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

    def parse_program(self, response):
        horaire = "soir" if ("soir" in response.url) else "" # distinguish day and night versions of programs
        program_name = response.xpath("//div[@class='formation-title']//h1/text()").get().replace("  ", " ").strip() 
        program_name = "{} - {}".format(program_name, horaire) if horaire else program_name
        program_id = "".join([keyword[0].upper() for keyword in program_name.split(" ") if keyword])  # no id it seems - make it up
        cycle = response.xpath("//div[@class='formation-banner-info-item'][1]/text()[2]").get().strip(" \n").lower()
        cycle = cycle if cycle in ["bac", "bachelier", "master"] else "other"
        campus = CAMPUS_MAPPING[cycle] # Anjou from bac2 to master2, Montgomery for the rest (see https://www.ichec.be/fr/nos-campus)
        ue_ids = response.css(".modal-link::text").getall()
        ue_ects = response.xpath("//div[@class='formation-tab-content structure']//table//td[5]/text()").getall()

        yield {
            "name": program_name,
            "id": program_id,
            "faculty": "Ecole de gestion et commerce",  # no explicit faculty
            "campus": campus, 
            "cycle": cycle,
            "courses": ue_ids,
            "ects": ue_ects,
            "url": response.url
        }