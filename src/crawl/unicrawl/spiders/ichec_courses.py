# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.ichec.be/fr/programmes"

LANGUAGE_DICT = {
    "Français": "fr",
    "Anglais": "en"
}


class ICHECCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for ICHEC Brussel Management School
    """

    name = "ichec-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ichec_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        links = response.xpath("//div[@class='formation-link']/a/@href").getall()
        yield from response.follow_all(links, self.parse_program)

    def parse_program(self, response):
        ues_links = response.xpath("//a[@class='modal-link']/@href").getall()
        yield from response.follow_all(ues_links, self.parse_ue)

    @staticmethod
    def parse_ue(response):

        ue_name = response.xpath("//h2[contains(text(), 'Intitulé')]/following::p[1]/text()").get()
        ue_id = response.xpath("//h2[contains(text(), 'Code')]/following::p[1]/text()").get()
        year = response.xpath("//h2[contains(text(), 'Année')]/following::p[1]/text()").get().replace(" - ", "-")
        teachers = response.xpath("//h2[contains(text(), 'Enseignant')]/following::p[1]/text()").getall()
        teachers = [t.lower().title() for t in teachers]
        lang = response.xpath("//h2[contains(text(), 'Langue')]/following::p[1]/text()").get()
        lang = [LANGUAGE_DICT[lang]]

        def get_section_text(section_name):
            texts = response.xpath(f"//h2[contains(., \'{section_name}\')]/following::p[1]/text()").getall()
            return "\n".join(texts).strip("\n")
        content = get_section_text("Description")
        goal = get_section_text("Objectifs et contribution")

        yield {
            "id": ue_id,
            "name": ue_name,
            "year": year,
            "languages": lang,
            "teachers": teachers,
            "url": response.url,
            "content": content,
            'goal': goal,
            'activity': '',
            'other': ''
        }
