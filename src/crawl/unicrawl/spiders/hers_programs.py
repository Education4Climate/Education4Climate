# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR

BASE_URL = "http://progcours.hers.be/cocoon/fac/fac{}"
DEPARTMENTS_CODES = {"M": "Département Paramédicale",
                     "P": "Département Pédagogique",
                     "E": "Département Economique",
                     "T": "Département Technique",
                     "S": "Département Social"}


class HERSProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Haute Ecole Robert Schuman
    """

    name = "hers-programs"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/hers_programs_{YEAR}.json',
    }

    def start_requests(self):
        for code in DEPARTMENTS_CODES.keys():
            base_dict = {"faculty": DEPARTMENTS_CODES[code]}
            yield scrapy.Request(BASE_URL.format(code), self.parse_main, cb_kwargs={'base_dict': base_dict})

    def parse_main(self, response, base_dict):
        # Get list of faculties
        programs_names = response.xpath(f"//a[@class='LienProg']/text()").getall()
        programs_links = response.xpath(f"//a[@class='LienProg']/@href").getall()
        programs_codes = [link.split("/")[-1].split("_")[0] for link in programs_links]
        programs_cycles = [name.split(" ")[0].lower() for name in programs_names]

        for name, code, link, cycle in zip(programs_names, programs_codes, programs_links, programs_cycles):
            cur_dict = {'name': name,
                        'id': code,
                        'cycle': cycle}
            yield response.follow(link, self.parse_program, cb_kwargs={'base_dict': {**base_dict, **cur_dict}})

    @staticmethod
    def parse_program(reponse, base_dict):

        ects = reponse.xpath("//td[contains(@class, 'ContColG')]/text()").getall()
        ects = [e for e in ects if e != '\xa0']
        # TODO: check if there are UEs
        courses_ids = reponse.xpath("//nobr/text()").getall()

        cur_dict = {"ects": ects,
                    "courses": courses_ids  # ,
                    # "ectsnb": len(ects),
                    # "coursesnb": len(courses_ids)
                    }

        yield {**base_dict, **cur_dict}
