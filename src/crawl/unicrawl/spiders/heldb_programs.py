# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from config.settings import YEAR

BASE_URL = "https://www.heldb.be/fr/formations-et-enseignement/formations/{}"
DEPARTMENTS_CODES = ["economique", "pedagogique", "technique"]


class HELDBProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole Lucia de Brouckère
    """

    name = "heldb-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(f'../../../../data/crawling-output/'
                                                              f'heldb_programs_{YEAR}.json')
    }

    def start_requests(self):
        for faculty_code in DEPARTMENTS_CODES:
            yield scrapy.Request(BASE_URL.format(faculty_code), self.parse_faculty)

    def parse_faculty(self, response):

        faculty = response.xpath("//h1/text()").get().strip("\t\n")
        program_links = response.xpath("//h4//a/@href").getall()
        # TODO: need to deal with 'long type'
        # TODO: need to add an id
        for link in program_links:
            yield response.follow(f"{link}/programme-cursus",
                                  self.parse_program, cb_kwargs={"faculty": faculty})

    @staticmethod
    def parse_program(response, faculty):

        program_name = response.xpath("//h1/text()").get().split("Programme du ")[1].strip("\t")
        cycle = program_name.split(" ")[0]
        ue_ids = response.xpath("//table[1]//tr[contains(@class, 'ue')]/td[@class='ue-acro']/text()").getall()
        ue_ects = response.xpath("//table[1]//tr[contains(@class, 'ue')]"
                                 "/td[contains(@class, 'ue-nbrcrd')]/text()").getall()
        ue_ects = list(map(int, map(float, ue_ects)))

        yield {"id": "",  # No id
               "name": program_name,
               "cycle": cycle,
               "faculty": faculty,
               "campus": '',
               "courses": ue_ids,
               "ects": ue_ects}
