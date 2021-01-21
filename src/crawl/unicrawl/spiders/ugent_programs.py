from abc import ABC

import scrapy

from config.settings import YEAR
from config.utils import cleanup

BASE_URL = f"https://studiegids.ugent.be/{YEAR}/NL/FACULTY/faculteiten.html"


class UgentProgramSpider(scrapy.Spider, ABC):
    name = 'ugent-programs'
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/ugent_programs_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        faculties_links = response.xpath("//aside//li[a[@target='_top']]/a/@href").getall()
        for link in faculties_links:
            # For now, parse only bacheloropleinding, masteropleidingen aansluitend op bacheloropleidingen and
            #  educatieve masteropleidingen
            for opleiding_code in ["BACH", "MABA", "EDMA"]:
                yield response.follow(f"{link}/{opleiding_code}/{opleiding_code}.html", self.parse_opleiding)
                exit()

    def parse_opleiding(self, response):

        # links = response.xpath("//div[@id='oase_heading_programmas']//li[@class='active']/a/@href").getall()
        links = response.xpath("//li[contains(@class, 'opleidingnaamlijst')]//a/@href").getall()

        codes = [link.split('.html')[0].split("/")[-1] for link in links]

        for code, link in zip(codes, links):
            base_dict = {"code": code}
            yield response.follow(link, self.parse_program, cb_kwargs={"base_dict": base_dict})
            exit()

    def parse_program(self, response, base_dict):

        program_name = response.xpath("//article//h1/text()").get()
        # Can have several faculties organising the class
        faculty = cleanup(response.xpath("//h2/text()").get()).split(",")
        cycle = ''
        if 'bachelor' in program_name or 'Bachelor' in program_name:
            cycle = 'bac'
        elif 'master' in program_name or 'Master' in program_name:
            cycle = 'master'

        # TODO: not sure that campus are specified anywhere
        campus = ''

        # TODO: seems a bit hardcore without the dynamic approach...
        main_code = response.xpath("//a[@target='hoofdframe' and contains(text(), 'Volledig programma')]/@href").get()

        cur_dict = {'name': program_name,
                    'cycle': cycle,
                    'campus': campus,
                    'faculty': faculty,
                    "courses": [],
                    "ects": []}

        yield response.follow(main_code, self.parse_course_sections, cb_kwargs={"base_dict": {**base_dict, **cur_dict}})

    @staticmethod
    def parse_course_sections(response, base_dict):

        sections = response.xpath("//span/i[contains(@class, 'glyphicon-minus')]/following::text()[1]").getall()
        sections = [s.split("\n")[0] for s in sections]

        # TODO: would need to do some recursive shit...

        courses_urls = response.xpath("//tr[contains(@class, 'rowclass')]//td[@class='cursus']/a").getall()
        courses_ids = [url.split(".pdf")[0].split("/")[-1] for url in courses_urls]
        ects = response.xpath("//tr[contains(@class, 'rowclass')]//td[@class='studiepunten']/text()").getall()
        ects = [int(e) for e in ects]

        cur_dict = {'courses': courses_ids,
                    'ects': ects,
                    'sections': sections}

        yield {**base_dict, **cur_dict}



