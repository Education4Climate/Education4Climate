from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'http://onderwijsaanbodmechelenantwerpen.thomasmore.be/opleidingen/n/'


class ThomasMoreProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Thomes More
    """

    name = 'thomasmore-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}thomasmore_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):

        # 'Faculties'
        faculties = response.xpath("//h3/a/text()").getall()

        # Get program groups for each faculty
        for faculty in faculties:
            program_group_links = response.xpath(f"//h3/a[text()='{faculty}']/following::div[1]"
                                                 f"//li[contains(@class, 'taal_n') or "
                                                 f"contains(@class, 'taal_e')]/a/@href").getall()
            for link in program_group_links:
                yield response.follow(link, self.parse_program_group, cb_kwargs={"faculty": faculty.split("More ")[1]})

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

        if 'bachelor' in program_name or 'Bachelor' in program_name:
            cycle = 'bac'
        elif 'postgrad' in program_name or 'Postgrad' in program_name:
            cycle = 'postgrad'
        elif 'graduaat' in program_name or 'Graduaat' in program_name:
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
