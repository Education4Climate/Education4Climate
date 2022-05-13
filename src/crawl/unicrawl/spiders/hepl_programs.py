# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = "https://www.hepl.be/fr/formations"


class HEPLProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Haute Ecole de la Province de Liège
    """

    name = "hepl-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}hepl_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):

        program_links = response.xpath("//div[@class='formation']/a/@href").getall()
        for link in program_links:
            yield response.follow(link, self.parse_secondary, cb_kwargs={'program_id': ''})

    def parse_secondary(self, response, program_id):

        link_to_list_of_courses = response.xpath("//a[@class='bloc-parcours-grille-cours']/@href").get()
        if link_to_list_of_courses is not None:
            sub_program_id = response.url.split("/")[-1].replace(f"-{YEAR}", "")
            program_id = f"{program_id}-{sub_program_id}" if program_id != '' else sub_program_id
            campus = response.xpath("//a[@class='site']/text()").get()
            yield response.follow(link_to_list_of_courses, self.parse_program,
                                  cb_kwargs={"url": response.url, "program_id": program_id, "campus": campus})
        else:
            links_sub_programs = response.xpath("//div[@class='formations-teaser']//a/@href").getall()
            program_id = response.url.split("/")[-1]
            for link in links_sub_programs:
                yield response.follow(link, self.parse_secondary, cb_kwargs={'program_id': program_id})

    @staticmethod
    def parse_program(response, url, program_id, campus):

        program_name = " ".join(cleanup(response.xpath("//span[@class='bottom']//text()").getall()))\
            .strip(" ").replace("  ", " ")
        faculty = response.xpath("//span[@class='top']/text()").getall()
        faculty = " ".join([f.strip(" \n\r") for f in faculty])

        cycle = response.xpath("//span[@class='diplome']/text()").get()
        if cycle == 'Bachelier':
            cycle = 'bac'
        elif cycle == 'Master':
            cycle = 'master'
        elif cycle == 'Spécialisation':
            cycle = 'other'  # TODO: à mettre dans other ou master ?

        courses = [link.split("/")[-1].split(".")[0] for link in
                   response.xpath("//tr[@class='info']/td[1]/a/@href").getall()]
        if len(courses) == 0:
            return
        ects = [int(e) for e in response.xpath("//tr[@class='info']/td[3]/text()").getall()]

        # It is not possible to differentiate directly the master courses from the bachelor once on the html pages
        #  so we do a manual removal of the courses which are in the wrong cycle (master and ohter = 2, bachelor = 1)
        courses_corrected, ects_corrected = [], []
        for c, e in zip(courses, ects):
            cycle_code = int(c.split('-')[1])
            if (cycle == 'bac' and cycle_code == 1) or (cycle == 'master' and cycle_code == 2) or \
                    (cycle == 'other' and cycle_code == 2):
                courses_corrected += [c.replace(f"-{YEAR}", '')]
                ects_corrected += [e]

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculties": [faculty],
            "campuses": [campus],
            "url": url,
            "courses": courses_corrected,
            "ects": ects_corrected
        }
