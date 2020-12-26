# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR

BASE_URL = "https://paysage.henallux.be/"


class HENALLUXProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole de Namur-Liège-Luxembourg
    """

    name = "henallux-programs"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/henallux_programs_{YEAR}.json',
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
        program_name = response.xpath("//span[@class='intituleOfficiel']/text()").get()
        faculty = response.xpath("//th[text()='Département']/following::td[1]/text()").get()
        cycle = response.xpath("//th[text()='Type']/following::td[1]/text()").get()
        # TODO: should we consider UE or 'activités d'apprentissage constitutives'
        #  -> maybe just for content? and teacher?
        ues = response.xpath("//li[@class='uetableau-menu']/a/text()").getall()
        ue_ids = [ue.split(" - ")[0].strip("\u00a0") for ue in ues]
        ects = response.xpath("//li[@class='uetableau-menu']/a/div[2]/text()").getall()

        yield {"name": program_name,
               "faculty": faculty,
               "cycle": cycle,
               "courses": ue_ids,
               "ects": ects  # ,
               # "nbcourses": len(ue_ids),
               # "nbects": len(ects)}
               }
