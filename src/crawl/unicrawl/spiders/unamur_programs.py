# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://directory.unamur.be/teaching/programmes"


class UNamurProgramSpider(scrapy.Spider, ABC):
    name = "unamur-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}unamur_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        # Get list of faculties
        faculties = response.xpath(f"//div[@id='tab-{YEAR}']//h3/a/text()").getall()
        for faculty in faculties:
            # For each faculty get its programs
            programs_links = response.xpath(
                f"//div[@id='tab-{YEAR}']//h3[a[contains(text(), \"{faculty}\")]]"
                f"//following::div[1]/div/a/@href").getall()
            programs_names = response.xpath(
                f"//div[@id='tab-{YEAR}']//h3[a[contains(text(), \"{faculty}\")]]"
                f"//following::div[1]/div/a/text()").getall()
            for program_name, programs_link in zip(programs_names, programs_links):

                if 'Doctorat' not in program_name and 'Cours' not in program_name:
                    if 'Bachelier' in program_name:
                        cycle = 'bac'
                    elif 'Master' in program_name:
                        cycle = 'master'
                    elif 'Certificat' in program_name:
                        cycle = 'certificate'
                    else:
                        cycle = 'other'

                    base_dict = {
                        "id": programs_link.split("/")[-2],
                        "name": program_name,
                        "cycle": cycle,
                        "faculties": [faculty],
                    }

                    yield response.follow(
                        programs_link,
                        self.parse_program,
                        cb_kwargs={'base_dict': base_dict}
                    )

    @staticmethod
    def parse_program(response, base_dict):
        codes = cleanup(response.xpath("//div[@id='cycle']//tr//td[@class='code']").getall())

        # Programs can be divided in 3, 2 or 1 blocks (or there is no ects)
        nb_blocks = 3
        ects = cleanup(response.xpath("//div[@id='cycle']//tr[not(@class='title')]"
                                      "//td[@class='credit three-column']").getall())
        if len(ects) == 0:
            nb_blocks = 2
            ects = cleanup(response.xpath("//div[@id='cycle']//tr[not(@class='title')]"
                                          "//td[@class='credit two-column']").getall())
        if len(ects) == 0:
            nb_blocks = 1
            ects = cleanup(response.xpath("//div[@id='cycle']//tr[not(@class='title')]"
                                          "//td[@class='credit one-column']").getall())
        ects_slimmed = ects
        if nb_blocks > 1:
            ects_slimmed = []
            # ects are given for each block -> keep only one value
            for i in range(len(codes)):
                course_ects = [ects[i * 3], ects[i * 3 + 1],
                               ects[i * 3 + 2]] if nb_blocks == 3 else [ects[i * 2],
                                                                        ects[i * 2 + 1]]
                course_ects = [e for e in course_ects if len(e)]
                # If there is still a different number of ects only keep the first one
                ects_slimmed += [list(set(course_ects))[0]]
        ects = [int(e) for e in ects_slimmed]

        cur_dict = {
            'campuses': [],  # campus information is obtained via the course crawler
            'url': response.url,
            'courses': codes,
            'ects': ects
            }

        yield {**base_dict, **cur_dict}
