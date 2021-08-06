# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.helmo.be/Formations/{}.aspx"
DEPARTMENTS = {"Département Economique et Juridique": "Economique",
               "Département Informatique et Technique": "Technique",
               "Département Paramédical": "Paramedical",
               "Département Pédagogique": "Pedagogique",
               "Département Social": "Social"}


class HELMOProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole Libre Mosane
    """

    name = "helmo-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}helmo_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        for dep_name, url_code in DEPARTMENTS.items():
            base_dict = {"faculty": dep_name}
            yield scrapy.Request(BASE_URL.format(url_code), self.parse_main, cb_kwargs={"base_dict": base_dict})

    def parse_main(self, response, base_dict):
        programs_links = response.xpath("//span[contains(text(), 'Menu')]//following::ul[1]//a/@href").getall()
        programs_names = response.xpath("//span[contains(text(), 'Menu')]//following::ul[1]//a/text()").getall()

        for i, (program_name, link) in enumerate(zip(programs_names, programs_links)):

            cycle = 'bac'
            if 'Master' in program_name:
                cycle = 'master'
            elif 'Spécialisation' in program_name:
                cycle = 'spe'

            cur_dict = {"id": f"{response.url.split('/')[-1].split('.')[0]} - {i}",
                        "name": program_name,
                        "cycle": cycle}

            yield response.follow(link, self.parse_program_main,
                                  cb_kwargs={'base_dict': {**cur_dict, **base_dict}})

    def parse_program_main(self, response, base_dict):

        campus = response.xpath("//h3[1]/span/text()").get()
        courses_list_links = response.xpath("//a[contains(text(), \"Programme d'études\")]/@href").getall()
        courses_list_names = response.xpath("//a[contains(text(), \"Programme d'études\")]/text()").getall()
        # Can have different options per course
        unique_name_links = set(zip(courses_list_names, courses_list_links))
        for name, link in unique_name_links:
            # Update name based on option
            cur_dict = {"name": base_dict["name"] + name.split("Programme d'études")[1],
                        "campus": campus}
            yield response.follow(link, self.parse_program_courses, cb_kwargs={"base_dict": {**base_dict, **cur_dict}})

    @staticmethod
    def parse_program_courses(response, base_dict):

        # Get list of courses that have a link
        # ue_names = response.xpath("//td[@colspan=2]/a/text()").getall()
        ue_ects = response.xpath("//td[@colspan=2]/a//following::td[1]/text()").getall()
        ue_urls = response.xpath("//td[@colspan=2]/a/@href").getall()
        ue_codes = [url.split("ue=")[1].split("#")[0] for url in ue_urls]
        ue_url_codes = [url.split("Formations/")[-1].strip("#a ") for url in ue_urls]

        cur_dict = {"url": response.url,
                    "courses": ue_codes,
                    "ects": ue_ects,
                    "courses_urls": ue_url_codes
                    }
        yield {**base_dict, **cur_dict}
