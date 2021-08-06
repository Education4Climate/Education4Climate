# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = f"https://ecolevirtuelle.provincedeliege.be/docStatique/ects/formationsHEPL-{YEAR}.html"


class HEPLProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole de la Province de Liège
    """

    name = "hepl-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}hepl_programs_{YEAR}_pre.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):

        number_of_rows = len(response.xpath("//tr[@class='list-row']").getall())
        for i in range(number_of_rows):
            row_txt = f"//tr[@class='list-row'][{i+1}]"
            faculty = response.xpath(f"{row_txt}/td[1]/span/text()").get()

            cycle = response.xpath(f"{row_txt}/td[2]/text()").get()
            cycle = 'bac' if cycle == 'Bachelier' else 'master'

            program_name = response.xpath(f"{row_txt}/td[3]/text()").get()

            sub_program_links = response.xpath(f"{row_txt}/td[position()>3]/a/@href").getall()
            program_id = "-".join(sub_program_links[0].split("/")[-1].split("-")[:2])

            base_dict = {
                "id": program_id,
                "name": program_name,
                "faculty": faculty,
                "cycle": cycle
            }

            for link in sub_program_links:
                yield response.follow(link, self.parse_sub_program, cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_sub_program(response, base_dict):

        base_dict["url"] = response.url

        line_txt = "//tr[@class='info']"
        courses_links = response.xpath(f"{line_txt}/td[1]/a/@href").getall()
        base_dict["courses"] = [link.split("/")[-1].replace(f"-{YEAR}.html", '') for link in courses_links]
        courses_ects = response.xpath(f"{line_txt}/td[3]/text()").getall()
        base_dict["ects"] = [int(e) for e in courses_ects]

        yield base_dict
