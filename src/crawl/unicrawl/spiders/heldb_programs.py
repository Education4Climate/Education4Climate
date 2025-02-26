# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.heldb.be/he-grilles"
DEPARTMENTS_NAMES = {
    0: "Sciences économiques et de gestion",
    1: "Sciences de l'éducation",
    2: "Sciences et techniques"
}


class HELDBProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Haute Ecole Lucia de Brouckère
    """

    name = "heldb-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}heldb_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):

        # Get links to programs
        programs_links = response.xpath("//body/div[1]//tr//td//a[1]/@href").getall()
        programs_names = response.xpath("//body/div[1]//tr//td//a[1]/text()[1]").getall()
        for (link, program_name) in zip(programs_links, programs_names):
            yield response.follow(link, self.parse_program, cb_kwargs={"program_name": program_name.strip("\n\t ")})

    @staticmethod
    def parse_program(response, program_name):

        program_id = response.url.split("/")[-1].split("-")[0]
        # program_name = response.xpath("//body/div[1]//strong[contains(text(), 'Section')]"
        #                               "/following::text()[1]").get().strip(" ")
        # if not program_name:
        #     print(f"No program name available for {response.url}")
        #     return
        program_subname = response.xpath("//body/div[1]//strong[contains(text(), 'Orientation')]"
                                         "/following::text()[1]").get()
        if program_subname:
            program_subname = program_subname.strip('\n ')
            # Some programs do not have options
            if len(program_subname) != 0:
                program_name += f" - {program_subname}"

        bloc = response.xpath("//body/div[1]//td[contains(text(), 'BLOC')]/text()").get()
        if bloc is None:
            print(f"No courses available for {program_name}")
            return
        bloc_number = int(bloc.split(" ")[1])
        cycle = 'bac' if bloc_number < 4 else 'master'

        faculty = response.xpath("//body/div[1]//strong[contains(text(), 'Domaine')]/following::text()[1]").get()

        main_text = '//body/div[1]'
        ue_ids = response.xpath(f"{main_text}//tr[contains(@class, 'ue') and"
                                f" td[contains(@class, 'bold')]]/td[2]/text()").getall()
        ue_ids = [ue.strip("\n ") for ue in ue_ids]
        ue_ects = response.xpath(f"{main_text}//tr[contains(@class, 'ue') and"
                                 f" td[contains(@class, 'bold')]]/td[4]/text()").getall()
        ue_ects = [int(e) for e in ue_ects]
        ue_urls_ids = response.xpath(f"{main_text}//tr[contains(@class, 'ue') and"
                                     f" td[contains(@class, 'bold')]]/@data-href").getall()
        ue_urls_ids = [ue.split("/")[-1] for ue in ue_urls_ids]

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculties": [faculty],
            "campuses": [],
            "url": response.url,
            "courses": ue_ids,
            "ects": ue_ects,
            "ue_urls_ids": ue_urls_ids
        }
