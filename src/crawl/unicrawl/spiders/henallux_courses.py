# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR

# TODO: check that we are not visiting several time the same courses


BASE_URL = "https://paysage.henallux.be/"
# TODO: check other languages
LANGUAGE_DICT = {"F": "fr"}


class HENALLUXCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for Haute Ecole de Namur-Liège-Luxembourg
    """

    name = "henallux-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/henallux_courses_{YEAR}.json',
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
            break

    def parse_aux(self, response):
        subprogram_links = response.xpath("//div[@class='content']//a/@href")
        for link in subprogram_links:
            yield response.follow(link, self.parse_program)

    def parse_program(self, response):
        ue_links = response.xpath("//li[@class='uetableau-menu']/a/@href").getall()
        for link in ue_links:
            yield response.follow(link, self.parse_ue)
            break

    @staticmethod
    def parse_ue(response):

        # TODO: should we consider UE or 'activités d'apprentissage constitutives'
        #  -> maybe just for content? and teacher?

        ue_name = response.xpath("//div[@class='intituleUE']/span/text()").get()
        ue_id = response.xpath("//span[@class='important']/text()").get()
        ue_div_txt = "//div[@class='identificationUE']"
        year = response.xpath(f"{ue_div_txt}//div[span[text()='Année académique']]/text()").get().split(": ")[1]
        dep = response.xpath(f"{ue_div_txt}//div[span[text()='Département']]/text()").get().split(": ")[1]
        ects = response.xpath(f"{ue_div_txt}//div[span[text()='Crédits']]/text()").get().split(": ")[1]
        language = response.xpath(f"{ue_div_txt}//div[span[text()=\"Langue d'enseignement\"]]/text()").get().split(": ")[1]
        # TODO: check if there cannot be different languages
        language = LANGUAGE_DICT[language]
        teachers = response.xpath(f"{ue_div_txt}//div[span[text()=\"Responsable de l'UE\"]]/text()").get().split(": ")[1]
        teachers = teachers.split(" - ")
        # TODO: to be checked if 1 corresponds to bachelier and if there can be other numbers
        cycle = response.xpath(f"{ue_div_txt}//div[span[text()='Cycle']]/text()").get().split(": ")[1]

        # TODO: content
        content = ""

        yield {"name": ue_name,
               "id": ue_id,
               "teacher": teachers,
               "year": year,
               "faculty": dep,
               "ects": ects,
               "language": language,
               "cycle": cycle,
               "campus": "",  # No campus
               "content": content
               }
