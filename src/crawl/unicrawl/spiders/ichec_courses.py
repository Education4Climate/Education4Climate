# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR

BASE_URL = "https://www.ichec.be/fr/programmes"
# TODO: check languages
LANGUAGE_DICT = {"Français": "fr",
                 "Anglais": "en"}


class ICHECCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for ICHEC Brussel Management School
    """

    name = "ichec-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/ichec_courses_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        links = response.xpath("//div[@class='formation-link']/a/@href").getall()
        for link in links:
            yield response.follow(link, self.parse_program)
            break

    def parse_program(self, response):
        ues_links = response.xpath("//div[@class='formation-tab-content structure']"
                                   "//table//a[@class='modal-link']/@href").getall()
        for link in ues_links:
            yield response.follow(link, self.parse_ue)
            break

    @staticmethod
    def parse_ue(response):

        ue_name = response.xpath("//h2[contains(text(), 'Intitulé')]/following::p[1]/text()").get()
        ue_id = response.xpath("//h2[contains(text(), 'Code')]/following::p[1]/text()").get()
        year = response.xpath("//h2[contains(text(), 'Année')]/following::p[1]/text()").get().replace(" - ", "-")
        # TODO: convert cycle code?
        cycle = response.xpath("//h2[contains(text(), 'Cycle')]/following::p[1]/text()").get()
        ects = response.xpath("//h2[contains(text(), 'Nombre de crédits')]/following::p[1]/text()").get()
        campus = response.xpath("//h2[contains(text(), 'Site')]/following::p[1]/text()").get()
        # TODO: check if there can be several teachers
        teachers = response.xpath("//h2[contains(text(), 'Enseignant')]/following::p[1]/text()").getall()
        lang = response.xpath("//h2[contains(text(), 'Langue')]/following::p[1]/text()").get()
        lang = LANGUAGE_DICT[lang]

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
