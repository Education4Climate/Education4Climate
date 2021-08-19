# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://paysage.henallux.be/"


class HENALLUXProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole de Namur-Liège-Luxembourg
    """

    name = "henallux-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}henallux_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        program_links = response.xpath("//section[@id='section_accueil']//a/@data-ref").getall()
        for link in program_links:
            if 'idCursusKey' in link:
                yield response.follow(link, self.parse_aux)
            else:
                yield response.follow(link, self.parse_program)

    def parse_aux(self, response):
        subprogram_links = response.xpath("//div[@class='content']//a/@href")
        for link in subprogram_links:
            yield response.follow(link, self.parse_program)

    @staticmethod
    def parse_program(response):
        program_id = [s for s in response.url.split("/") if s.isnumeric()][0]
        program_name = response.xpath("//span[@class='intituleOfficiel']/text()").get()
        faculty = response.xpath("//th[text()='Département']/following::td[1]/text()").get()
        cycle = response.xpath("//th[text()='Type']/following::td[1]/text()").get()
        if cycle == 'Bachelier':
            cycle = 'bac'
        elif cycle == 'Master':
            cycle = 'master'
        else:
            cycle = 'other'
        ues = response.xpath("//li[@class='uetableau-menu']/a/text()").getall()
        ue_ids = [ue.split(" - ")[0].strip("\u00a0") for ue in ues]
        ue_links = response.xpath("//li[@class='uetableau-menu']/a/@href").getall()
        ue_links_codes = [ue_link.split("idUe/")[1].split("/")[0] for ue_link in ue_links]
        ects = [int(float(e)) for e in response.xpath("//li[@class='uetableau-menu']/a/div[2]/text()").getall()]

        yield {"id": program_id,
               "name": program_name,
               "faculty": faculty,
               "cycle": cycle,
               "campus": "",
               "url": response.url,
               "courses": ue_ids,
               "ects": ects,
               "courses_url_codes": ue_links_codes
               }
