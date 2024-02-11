# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = f"https://plus.ecam.be/public/cursus/{YEAR}/" + "{}"

# Do not include BAC because included in the masters
PROGRAM_CODES = ["MAU", "MCO", "MEM", "MEO", "MGA", "MGE", "MIN", "MIS"]


class ECAMProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for ECAM Bruxelles
    """

    name = "ecam-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ecam_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        for program_id in PROGRAM_CODES:
            link = BASE_URL.format(program_id)
            yield scrapy.Request(link, self.parse_program, cb_kwargs={"program_id": program_id})

    @staticmethod
    def parse_program(response, program_id):

        if program_id != "MIC":
            program_name = response.xpath("//h4/text()").get()
            ue_ids = response.xpath("//table//a/text()").getall()
            ue_ids = [ue_id.split(" ")[0].strip(" \n") for ue_id in ue_ids]
        else:
            program_name = response.xpath("//h3/text()").get()
            ue_ids = response.xpath("//table//a/text()").getall()
            ue_ids = [ue_id.split(":")[0].strip(" \n") for ue_id in ue_ids]
        ues_ects = response.xpath("//table//tr/td[2]/text()").getall()
        ues_ects = [int(e) for e in ues_ects]
        program_name = program_name.strip("\n (")

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": "master",  # master programs with shared bachelor
            "faculties": ["Ingénieur industriel"],  # only one faculty
            "campuses": ["Campus Woluwe"],  # only one campus
            "url": response.url,
            "courses": ue_ids,
            "ects": ues_ects
        }
