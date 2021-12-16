# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.heldb.be/fr"
DEPARTMENTS_NAMES = {
    0: "Sciences économiques et de gestion",
    1: "Sciences de l'éducation",
    2: "Sciences et techniques"
}


class HELDBProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Haute Ecole Lucia de Brouckère
    """

    name = "heldb-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}heldb_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_faculty)

    def parse_faculty(self, response):

        for faculty_id, faculty in DEPARTMENTS_NAMES.items():
            # A bit barbaric
            program_links = set(response.xpath(f"//tbody//td[{faculty_id+1}]//a/@href").getall())
            program_links = [link for link in program_links if len(link.split("/")) > 5]
            for program_id, link in enumerate(program_links):
                link = f"{link}/programme-cursus" if 'dietetique' not in link else f"{link}/programme-du-cursus"
                yield response.follow(link, self.parse_program,
                                      cb_kwargs={"program_id": f"{faculty_id}-{program_id}",
                                                 "faculty": faculty})

    @staticmethod
    def parse_program(response, program_id, faculty):

        program_name = response.xpath("//h1/text()").get().split("Programme du ")[1].strip("\t")

        cycle = program_name.split(" ")[0]
        cycle = 'bac' if cycle == 'Bachelier' else 'master'

        if cycle == 'master':
            program_name += ' en Biochimie' if 'biochimie' in response.url else ' en Chimie'

        ue_ids = response.xpath("//table[1]//tr[contains(@class, 'ue')]/td[@class='ue-acro']/text()").getall()
        ue_ects = response.xpath("//table[1]//tr[contains(@class, 'ue')]"
                                 "/td[contains(@class, 'ue-nbrcrd')]/text()").getall()
        ue_ects = list(map(int, map(float, ue_ects)))
        ue_links = response.xpath("//table[1]//tr[contains(@class, 'ue')]/td[@class='ue-lib']/a[1]/@href").getall()
        ue_urls_ids = [link.split("/")[-1] for link in ue_links]

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculties": [faculty],
            "campuses": [],
            "url": response.url,
            "courses": ue_ids,
            "ects": ue_ects,
            "ue_urls_ids": ue_urls_ids
        }
