# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.ecam.be/{}"
PROGRAM_CODE_LIST = ["MAU", "MCO", "MEM", "MEO", "MGE", "MIN", "MIS", "MIC"]


class ECAMProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for ECAM Bruxelles
    """

    name = "ecam-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ecam_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        for code in PROGRAM_CODE_LIST:
            base_dict = {"id": code}
            yield scrapy.Request(BASE_URL.format(code), self.parse_program, cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_program(response, base_dict):

        program_name = response.xpath("//h3/text()").get().split(" (")[0]
        ue_ids = response.xpath("//table//a/text()").getall()
        ue_ids = [ue_id.split(":")[0].strip(" \n") for ue_id in ue_ids]
        ues_ects = response.xpath("//table//tr/td[2]/text()").getall()

        yield {
            "name": program_name,
            "id": base_dict['id'],
            "cycle": "master", # master programs with shared bachelor
            "campus": "Campus Woluwe", # only one campus
            "faculty": "Ingénieur industriel",  # only one faculty
            "courses": ue_ids,
            "ects": ues_ects,
            "url": response.url
        }
