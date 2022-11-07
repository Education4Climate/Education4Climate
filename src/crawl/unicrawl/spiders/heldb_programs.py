# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.heldb.be/wpfiches/#"
DEPARTMENTS_NAMES = {
    0: "Sciences économiques et de gestion",
    1: "Sciences de l'éducation",
    2: "Sciences et techniques"
}

ACAD_YEARS_CODES = {
    2022: '9'
}


class HELDBProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Haute Ecole Lucia de Brouckère
    """

    name = "heldb-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}heldb_programs_{YEAR}_pre.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):

        # Get links to programs
        programs_links = response.xpath("//div[@class='dropdown-menu']/a/@href").getall()
        programs_campuses = response.xpath("//div[@class='dropdown-menu']/a/span/text()").getall()
        for link, campus in zip(programs_links, programs_campuses):
            yield response.follow(link + ACAD_YEARS_CODES[YEAR], self.parse_program, cb_kwargs={'campus': campus})

    @staticmethod
    def parse_program(response, campus):

        program_id = response.url.split("sodid=")[1].split("&")[0]
        if len(program_id) == 0:
            return
        program_name = response.xpath("//b[contains(text(), 'Section')]/following::text()[1]").get()
        program_subname = response.xpath("//b[contains(text(), 'Option')]/following::text()[1]").get()
        if program_subname:
            program_subname = program_subname.strip('\n ')
            # Some programs do not have options
            if len(program_subname) != 0:
                program_name += f" - {program_subname}"
        # Special case for 'Sciences de l'Ingénieur Industriel'
        if "Sciences de l'Ingénieur Industriel" in program_name:
            sub_programs = response.xpath("//b[contains(text(), 'Option')]/following::text()[1]").getall()
            if any(['Biochimie' in sub_program for sub_program in sub_programs]):
                program_name = "Sciences de l'Ingénieur Industriel - Biochimie"
                program_id = "24"
            else:
                program_name = "Sciences de l'Ingénieur Industriel - Chimie"
                program_id = "27"

        bloc = response.xpath("//th[contains(text(), 'BLOC')]/text()").get()
        bloc_number = int(bloc.split(" ")[1])
        cycle = 'bac' if bloc_number < 4 else 'master'

        faculty = response.xpath("//b[contains(text(), 'Domaine')]/following::text()[1]").get()

        main_text = "//div[contains(@class, 'container-fluid')]"
        ue_ids = response.xpath(f"{main_text}//tr[contains(@class, 'ue')"
                                f" and contains(@class, 'bold')]/td[2]/text()").getall()
        ue_ids = [ue.strip("\n ") for ue in ue_ids]
        ue_ects = response.xpath(f"{main_text}//tr[contains(@class, 'bold')]/td[5]/text()").getall()
        ue_urls_ids = response.xpath(f"{main_text}//tr[contains(@class, 'ue')]/@data-href").getall()
        ue_urls_ids = [ue.split("/")[-1] for ue in ue_urls_ids]

        # ue_ids, ue_ects, ue_urls_ids = list(zip(*set(zip(ue_ids, ue_ects, ue_urls_ids))))

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculties": [faculty],
            "campuses": [campus],
            "url": response.url,
            "courses": ue_ids,
            "ects": ue_ects,
            "ue_urls_ids": ue_urls_ids
        }
