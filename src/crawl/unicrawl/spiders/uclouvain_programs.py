# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

UCLOUVAIN_URL = f"https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-{YEAR}.html"


class UCLouvainProgramSpider(scrapy.Spider, ABC):
    name = "uclouvain-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}uclouvain_programs_{YEAR}_pre.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(url=UCLOUVAIN_URL, callback=self.parse_main)

    def parse_main(self, response):

        # Get faculty
        faculties = response.xpath("//b/text()").getall()

        # Parse programs per faculty
        for faculty in faculties:
            program_links = response.xpath(f"//ul[header/a/b[contains(text(), \"{faculty}\")]]//li//a/@href").getall()
            for link in program_links:
                yield response.follow(link, self.parse_program, cb_kwargs={'faculty': faculty})

    def parse_program(self, response, faculty):

        program_id_and_campus = response.xpath("//p[@id='offer-page-subtitle']/text()").get().split('\n')
        program_id = program_id_and_campus[0]
        # If no campus is specified, consider it's Louvain-La-Neuve
        campus = program_id_and_campus[3].strip(" ") if len(program_id_and_campus) > 3 else 'Louvain-La-Neuve'

        program_name = response.xpath("//div[@id='offer-page-title']/a/text()").get()

        if 'Bachelier' in program_name:
            cycle = 'bac'
        elif 'Master' in program_name:
            cycle = 'master'
        elif 'Certificat' in program_name or 'Attestation' in program_name:
            cycle = 'certificate'
        else:  # 'Approfondissement', 'Agrégation', 'Filière', 'Mineure'
            cycle = 'other'

        cur_dict = {"id": program_id,
                    "name": program_name,
                    "faculty": faculty,
                    "campus": campus,
                    "cycle": cycle,
                    "url": response.url}

        # TODO: peut aussi y avoir 'Finalités' où il faut parse une autre page avant d'arriver au programme spécialisé
        pages_names = ["Tronc commun", "Programme par matière", "Finalité spécialisée", "Programme"]
        for page_name in pages_names:
            course_list_link = \
                response.xpath(f"//a[@class='dropdown-toggle' and contains(text(), 'Programme détaillé')]"
                               f"/following::ul[1]//a[text()=\"{page_name}\"]/@href").get()
            if course_list_link is not None:
                yield response.follow(course_list_link, self.parse_course_list,
                                      cb_kwargs={"base_dict": cur_dict})

    @staticmethod
    def parse_course_list(response, base_dict):

        courses_ids = response.xpath("//tr[@class='composant-ligne1']/td[1]/span/text()").getall()
        if len(courses_ids) == 0:
            return
        # Missing credit with one program
        if base_dict['id'] == "RXU2CE":
            courses_ids = courses_ids[:-1]

        ects = response.xpath("//tr[@class='composant-ligne1']/td[5][contains(text(), 'crédit')]/text()").getall()
        ects = [int(cleanup(e).strip(" crédits")) for e in ects]

        cur_dict = {"courses": courses_ids,
                    "ects": ects}

        yield {**base_dict, **cur_dict}



