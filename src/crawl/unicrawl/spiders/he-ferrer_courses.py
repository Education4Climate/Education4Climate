# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR

BASE_URL = "https://fiches-ue.icampusferrer.eu/locked_list.php"

# TODO: checker langues
LANGUAGES_DICT = {"Français": "fr",
                  "Anglais": "en"}


class HECHCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for Haute Ecole Francisco Ferrer
    """
    name = "he-ferrer-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/he-ferrer_courses_{YEAR}.json',
    }

    def start_requests(self):

        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        ue_links = response.xpath("//tr//a/@href").getall()
        for link in ue_links:
            yield response.follow(link, self.parse_ue)

    def parse_ue(self, response):
        name = response.xpath("//h3/text()").get()
        year = response.xpath("//h5[1]/text()").get().split(":")[1].strip(" ")
        faculty = response.xpath("//h5[contains(text(), 'Catégorie')]/text()").get()
        code = response.xpath("//td[contains(text(), 'Code')]//following::strong[1]/text()").get()
        teacher = response.xpath("//td[contains(text(), \"Responsable de l'UE\")]//following::span[1]/text()").get()
        program = response.xpath("//h2/text()").get()
        ects = response.xpath("//td[contains(text(), 'Crédits ECTS')]//following::strong[1]/text()").get()
        cycle = response.xpath("//td[contains(text(), 'Cycle')]//following::strong[1]/text()").get()
        language = response.xpath("//td[contains(text(), \"Langue d'enseignement et d'évaluation\")]"
                                  "//following::strong[1]/text()").get()
        language = LANGUAGES_DICT[language]

        # TODO content
        content = ""

        yield {"code": code,
               "name": name,
               "teacher": teacher,
               "program": program,
               "cycle": cycle,
               "ects": ects,
               "year": year,
               "faculty": faculty,
               "language": language,
               "content": content,
               "url": response.url}
