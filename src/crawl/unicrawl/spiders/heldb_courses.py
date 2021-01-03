# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.utils import cleanup
from config.settings import YEAR

BASE_URL = "http://www.heldb.be/fr/formations-et-enseignement"
# TODO: check languages
LANGUAGE_DICT = {"Français": "fr"}

class HELDBCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for Haute Ecole Lucia de Brouckère
    """

    name = "heldb-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/heldb_courses_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        program_links = response.xpath("//ul[@class='ListeFormations']//a/@href").getall()
        for link in program_links:
            yield response.follow(f"{link}/programme-cursus", self.parse_program)
            break

    def parse_program(self, response):

        ue_links = response.xpath("//table[1]//tr[contains(@class, 'ue')]/td[@class='ue-lib']/a/@href").getall()
        for link in ue_links:
            yield response.follow(link, self.parse_ue)
            break

    @staticmethod
    def parse_ue(response):

        ue_name = response.xpath("//div[@name='titleue']//h1/text()").get()
        div_txt = "//div[contains(@class, 'container-fluid')]"
        ue_id = response.xpath(f"{div_txt}//span[contains(text(), 'Acronyme')]/following::span[1]/text()").get()
        lang = response.xpath(f"{div_txt}//span[contains(text(), \"Langue(s) d'enseignement\")]"
                              f"/following::span[1]/text()").get()
        lang = LANGUAGE_DICT[lang.strip(" \n")]
        ects = response.xpath(f"{div_txt}//span[contains(text(), 'Nombre de crédits ECTS')]"
                              f"/following::span[1]/text()").get().split("(")[0].strip(" ")
        teachers = response.xpath(f"{div_txt}//strong[text()='Enseignant responsable : ']"
                                  f"/following::a[1]/text()").getall()
        sup_teachers = response.xpath(f"{div_txt}//strong[contains(text(), \"Autre(s) enseignant(s) de l'UE\")]"
                                      f"/following::a[1]/text()").getall()
        teachers += sup_teachers
        year = cleanup(response.xpath(f"{div_txt}//div[@id='anac']//i").get()).split("Année académique ")[1]
        # TODO: check if 1er cycle -> bachelier?
        cycle = response.xpath(f"{div_txt}//span[contains(text(), 'Niveau du cycle')]"
                               f"/following::span[1]/text()").get().strip("\n ")

        # TODO: check if there is another one
        campus = "Anderlecht"

        # TODO: content
        content = ""

        yield {"name": ue_name,
               "id": ue_id,
               "teacher": teachers,
               "year": year,
               "ects": ects,
               "language": lang,
               "cycle": cycle,
               "campus": campus,
               "content": content}
