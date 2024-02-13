# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = f"https://paysage.henallux.be/fr/{YEAR}"
PROGRAM_URL = "https://paysage.henallux.be/fr/{}/{}/" + f"{YEAR}"


class HENALLUXProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Haute Ecole de Namur-Liège-Luxembourg
    """

    name = "henallux-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}henallux_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):

        program_ids = response.xpath("//div[@class='cursus']/@id").getall()
        program_data_u = response.xpath("//div[@class='cursus']/@data-u").getall()
        for program_id, data_u in zip(program_ids, program_data_u):
            if int(data_u) == 0:
                link = PROGRAM_URL.format('dep-cursus', program_id)
                yield response.follow(link, self.parse_aux, cb_kwargs={'program_id': program_id})
            else:
                link = PROGRAM_URL.format('cursus', program_id)
                yield response.follow(link, self.parse_program, cb_kwargs={'program_id': program_id})

    def parse_aux(self, response, program_id):

        subprogram_ids = response.xpath("//div[contains(@class, 'orientation')]/@id").getall()
        for subprogram_id in subprogram_ids:
            updated_program_id = f"{program_id}-{subprogram_id}"
            link = PROGRAM_URL.format('cursus', subprogram_id)
            yield response.follow(link, self.parse_program, cb_kwargs={'program_id': updated_program_id})

    @staticmethod
    def parse_program(response, program_id):

        program_name = response.xpath("//h3/text()").get()
        program_name = program_name.strip("- ")
        faculty_campus = response.xpath("//div[span[text()='Département']]/text()").get().strip(" :")
        if faculty_campus == "Département paramédical Sainte-Elisabeth":
            faculty = "Département paramédical"
            campuses = ["Sainte-Elisabeth"]
        elif faculty_campus == "Département pédagogique de Namur - Site de Champion":
            faculty = "Département pédagogique"
            campuses = ["Namur - Site de Champion"]
        elif faculty_campus == "Département pédagogique de Namur - Site de Malonne":
            faculty = "Département pédagogique"
            campuses = ["Namur - Site de Malonne"]
        elif faculty_campus == "Départements sociaux de Cardijn et de Namur":
            faculty = "Département social"
            campuses = ["Cardijn", "Namur"]
        elif faculty_campus == "Département technique d'Arlon":
            faculty = "Département technique"
            campuses = ["Arlon"]
        elif ' de ' in faculty_campus:
            faculty, campus = faculty_campus.split(" de ")
            campuses = [campus]
        elif ' - ' in faculty_campus:
            faculty, campus = faculty_campus.split(" - ")
            campuses = [campus]
        else:
            faculty = faculty_campus
            campuses = []

        if 'Spécialisation' in program_name:
            cycle = 'other'
        elif 'Master' in program_name:
            cycle = 'master'
        else:
            cycle = 'bac'

        main_lines_txt = "//table//tr[contains(@class, 'true') and contains(@class, 'unit')]"
        ue_ids = response.xpath(f"{main_lines_txt}/td[1]/text()").getall()
        ue_links_codes = response.xpath(f"{main_lines_txt}/@id").getall()
        ue_links_codes = [code.strip("tr") for code in ue_links_codes]
        ects = [int(float(e)) for e in response.xpath(f"{main_lines_txt}/td[3]/text()").getall()]

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculties": [faculty],
            "campuses": campuses,
            "url": response.url,
            "courses": ue_ids,
            "ects": ects,
            "courses_url_codes": ue_links_codes
        }
