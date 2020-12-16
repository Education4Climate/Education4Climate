# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR

BASE_URL = "http://www.heldb.be/fr/formations-et-enseignement"


class HELDBProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole Lucia de Brouckère
    """

    name = "heldb-programs"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/heldb_programs_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        program_links = response.xpath("//ul[@class='ListeFormations']//a/@href").getall()
        for link in program_links:
            category = link.split("/")[-2]
            base_dict = {"faculty": f"Catégorie {category}"}
            yield response.follow(f"{link}/programme-cursus",
                                  self.parse_program, cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_program(response, base_dict):

        program_name = response.xpath("//h1/text()").get().split("Programme du ")[1].strip("\t")
        cycle = program_name.split(" ")[0]
        ue_ids = response.xpath("//table[1]//tr[contains(@class, 'ue')]/td[@class='ue-acro']/text()").getall()
        ue_ects = response.xpath("//table[1]//tr[contains(@class, 'ue')]"
                                 "/td[contains(@class, 'ue-nbrcrd')]/text()").getall()
        ue_ects = list(map(int, map(float, ue_ects)))

        cur_dict = {"name": program_name,
                    "id": "",  # No id
                    "courses": ue_ids,
                    "ects": ue_ects,
                    "cycle": cycle}

        yield {**cur_dict, **base_dict}
