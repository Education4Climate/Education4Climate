# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "http://progcours.heaj.be/cocoon/fac/fac{}"
DEPARTMENTS_CODES = {"E": "Département Economique",
                     "P": "Département Pédagogique",
                     "T": "Département Technique"}


class HEAJProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole Albert Jacquard
    """

    name = "heaj-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}heaj_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        for code in DEPARTMENTS_CODES.keys():
            yield scrapy.Request(BASE_URL.format(code), self.parse_main,
                                 cb_kwargs={'faculty': DEPARTMENTS_CODES[code]})

    def parse_main(self, response, faculty):
        # Get list of faculties
        programs_names = response.xpath(f"//a[@class='LienProg']/text()").getall()
        programs_links = response.xpath(f"//a[@class='LienProg']/@href").getall()
        programs_codes = [link.split("/")[-1].split("_")[0] for link in programs_links]
        programs_cycles = [name.split(" ")[0].lower() for name in programs_names]

        for program_name, code, link, cycle in zip(programs_names, programs_codes, programs_links, programs_cycles):

            if 'bachelier' in cycle:
                cycle = 'bac'
            elif 'master' in cycle:
                cycle = 'master'
            else:
                cycle = 'other'

            base_dict = {'id': code,
                         'name': program_name,
                         'cycle': cycle,
                         'faculty': faculty,
                         'campus': ''}
            yield response.follow(link, self.parse_program, cb_kwargs={'base_dict': base_dict})

    @staticmethod
    def parse_program(response, base_dict):

        ects = response.xpath("//td[contains(@class, 'ContColG')]/text()").getall()
        ects = [int(e) for e in ects if e != '\xa0']
        courses_ids = response.xpath("//nobr/text()").getall()

        cur_dict = {"url": response.url,
                    "courses": courses_ids,
                    "ects": ects
                    }

        yield {**base_dict, **cur_dict}
