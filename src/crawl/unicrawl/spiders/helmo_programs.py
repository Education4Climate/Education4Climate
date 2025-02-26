# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.helmo.be/fr/formations"


class HELMOProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Haute Ecole Libre Mosane
    """

    name = "helmo-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}helmo_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):

        programs_links = response.xpath("//a[contains(@class, 'studyCard__link')]/@href").getall()
        for program_link in programs_links:
            yield response.follow(program_link, self.parse_program_link)

    def parse_program_link(self, response):

        program_link = response.xpath("//main//a[contains(@href, '/programme') "
                                      "and contains(text(), 'Programme')]/@href").get()

        if program_link:
            yield response.follow(program_link, self.parse_program)
        else:
            print(f"Could not find program description for: {response.url}")


    @staticmethod
    def parse_program(response):

        program_id = response.url.split("/")[-2].split("-")[0]
        program_id_url = "/".join(response.url.split("/")[-2:])
        program_name = response.xpath("//h1/text()").get()

        cycle = 'other'
        if 'master' in program_name.lower():
            cycle = 'master'
        elif 'bachelier' in program_name.lower():
            cycle = 'bac'

        campuses = response.xpath("//div[@class='studyInfo__location']//a/text()").getall()
        campuses = [campus.strip("HELMo / ").strip(", ") for campus in campuses]
        faculty = response.xpath("//dl[contains(@class, 'studyInfo__meta')]//dd/text()").get()

        ue_urls = response.xpath("//section[h2[contains(text(), 'Programme d')]]//h5/a/@href").getall()
        ue_codes = [url.split("/")[-1] for url in ue_urls]
        ue_ects = response.xpath("//section[h2[contains(text(), 'Programme d')]]"
                                 "//li[h5[a]]//span[contains(text(), 'cr')]/text()").getall()
        ue_ects = [int(ects.split("cr")[0]) for ects in ue_ects]

        if len(ue_codes) != len(ue_ects):
            print(len(ue_codes), len(ue_ects))
            print(response.url)

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculties": [faculty],
            "campuses": campuses,
            "url": response.url,
            "courses": ue_codes,
            "ects": ue_ects,
            "id_url": program_id_url
        }
