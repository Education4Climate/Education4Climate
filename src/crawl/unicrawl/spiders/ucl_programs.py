# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from config.settings import YEAR
from config.utils import cleanup

UCL_URL = f"https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-{YEAR}.html"


class UCLProgramSpider(scrapy.Spider, ABC):
    name = "ucl-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(f'../../../../data/crawling-output/'
                                                              f'ucl_programs_{YEAR}_pre.json'),
    }

    def start_requests(self):
        base_url = UCL_URL
        yield scrapy.Request(url=base_url, callback=self.parse_main)

    def parse_main(self, response):
        faculties_links = response.xpath("//h5//a/@href").getall()
        for href in faculties_links:
            yield response.follow(href, self.parse_faculty)

    def parse_faculty(self, response):
        faculty_name = response.xpath("//div[contains(@class, 'block-title')]//h1/text()").get()
        faculty_name = faculty_name.replace("Formations de la ", "")
        base_dict = {"faculty": faculty_name}

        programs_links = response.xpath("//main//li/a/@href").getall()
        for href in programs_links:
            yield response.follow(href, self.parse_program, cb_kwargs={"base_dict": base_dict})

    def parse_program(self, response, base_dict):

        program_id = response.xpath("//p[@id='offer-page-subtitle']/text()").get().split('\n')[0]
        program_name = response.xpath("//div[@id='offer-page-title']/a/text()").get()
        campus = response.xpath("//span[@class='location']/text()").get()
        campus = "" if campus is None else campus.strip(" ")

        if 'Bachelier' in program_name:
            cycle = 'bac'
        elif 'Mineure' in program_name:
            cycle = 'minor'
        elif 'Master' in program_name:
            cycle = 'master'
        elif 'Certificat' in program_name or 'Attestation' in program_name:
            cycle = 'certificate'
        else:  # 'Approfondissement', 'Agrégation', 'Filière'
            cycle = 'other'

        cur_dict = {"id": program_id,
                    "name": program_name,
                    "campus": campus,
                    "cycle": cycle}

        # TODO: this creates a problem as we will have mulitple lines for the same program. How to correct that?
        pages_names = ["Tronc commun", "Programme par matière", "Finalité spécialisée", "Programme"]
        for page_name in pages_names:
            course_list_link = \
                response.xpath(f"//a[@class='dropdown-toggle' and contains(text(), 'Programme détaillé')]"
                               f"/following::ul[1]//a[text()=\"{page_name}\"]/@href").get()
            if course_list_link is not None:
                yield response.follow(course_list_link, self.parse_course_list,
                                      cb_kwargs={"base_dict": {**cur_dict, **base_dict}})

    @staticmethod
    def parse_course_list(response, base_dict):

        courses_ids = response.xpath("//tr[@class='composant-ligne1']/td[1]/span/text()").getall()
        if len(courses_ids) == 0:
            return
        ects = response.xpath("//tr[@class='composant-ligne1']/td[5][contains(text(), 'crédit')]/text()").getall()
        ects = [int(cleanup(e).strip(" crédits")) for e in ects]

        cur_dict = {"courses": courses_ids,
                    "ects": ects}

        yield {**base_dict, **cur_dict}



