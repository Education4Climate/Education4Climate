from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'https://onderwijsaanbod.limburg.ucll.be/opleidingen/n/'


class UCLLProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for UC Leuven-Limburg
    """

    name = 'ucll-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ucll_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):

        # 'Faculties'
        faculties = response.xpath("//h3/a/text()").getall()

        # Get program groups for each faculty
        for faculty in faculties:
            faculty_simple = faculty.split("Programma ")[1].split(' UC Limburg')[0]
            program_group_links = response.xpath(f"//h3/a[text()='{faculty}']/following::div[1]"
                                                 f"//li[contains(@class, 'taal_n') or "
                                                 f"contains(@class, 'taal_e')]/a/@href").getall()
            for link in program_group_links:
                yield response.follow(link, self.parse_program_group,
                                      cb_kwargs={"faculty": faculty_simple})

    def parse_program_group(self, response, faculty):

        links = response.xpath("//div[@id='oase_heading_programmas']//li[@class='active']/a/@href").getall()
        codes = [link.split('.')[0] for link in links]

        for code, link in zip(codes, links):
            yield response.follow(link, self.parse_program, cb_kwargs={"program_id": code, "faculty": faculty})

    @staticmethod
    def parse_program(response, program_id, faculty):

        program_name = response.xpath("//h1/text()").get()
        campuses = []
        if '(' in program_name:
            campuses = [program_name.split('(')[-1].split(')')[0]]

        if 'bachelor' in program_name.lower() or 'PBA' \
                in program_name or 'BNB' in program_name or 'EBA' in program_name:
            cycle = 'bac'
        elif 'postgraduaat' in program_name.lower() or 'PG' in program_name:
            cycle = 'postgrad'
        elif 'graduaat' in program_name.lower():
            cycle = 'grad'
        else:
            cycle = 'other'

        courses = response.xpath("//tr[contains(@class, 'opo_row')]//td[@class='code']/text()").getall()
        courses_url = response.xpath("//td[@class='opleidingsonderdeel']/a/@href").getall()
        courses_url = [c.split("/syllabi/")[1].split('.htm')[0] for c in courses_url]
        ects = response.xpath("//tr[contains(@class, 'opo_row')]//td[@class='sp']/text()").getall()
        ects = [int(e.split(" ")[0]) for e in ects]
        # Get list of unique courses and ects
        courses, courses_url, ects = zip(*set(zip(courses, courses_url, ects)))

        yield {
            'id': program_id,
            'name': program_name,
            'cycle': cycle,
            'faculties': [faculty],
            'campuses': campuses,
            'url': response.url,
            'courses': courses,
            'ects': ects,
            'courses_urls': courses_url
        }
