from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'https://onderwijsaanbod.kuleuven.be/opleidingen/n/'


class KULeuvenProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for KULeuven
    """

    name = 'kuleuven-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}kuleuven_programs_{YEAR}.json').as_uri()
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
                yield response.follow(link, self.parse_program_group, cb_kwargs={"faculty": faculty})

    def parse_program_group(self, response, faculty):

        links = response.xpath("//div[@id='oase_heading_programmas']//li[@class='active']/a/@href").getall()
        codes = [link.split('.')[0] for link in links]

        for code, link in zip(codes, links):
            yield response.follow(link, self.parse_program,
                                  cb_kwargs={"program_id": code, 'faculty': faculty})

    @staticmethod
    def parse_program(response, program_id, faculty):

        program_name = response.xpath("//h1/text()").get()

        campus = ''
        if '(' in program_name:
            campus = program_name.split('(')[-1].split(')')[0]

        cycle = 'other'
        if 'bachelor' in program_name or 'Bachelor' in program_name:
            cycle = 'bac'
        elif 'postgraduaat' in program_name or 'Postgraduaat' in program_name or \
                'postgraduate' in program_name or 'Postgraduate' in program_name:
            cycle = 'postgrad'
        elif 'graduaat' in program_name or 'Graduaat' in program_name:
            cycle = 'grad'
        elif 'master' in program_name or 'Master' in program_name:
            cycle = 'master'
        elif 'doctor' in program_name or 'Doctor' in program_name:
            cycle = 'doctor'

        courses = response.xpath("//tr[contains(@class, 'opo_row')]//td[@class='code']/text()").getall()
        # If there are no courses to crawl, discard the program
        if len(courses) == 0:
            return
        courses_url = response.xpath("//td[@class='opleidingsonderdeel']/a/@href").getall()
        courses_url = [c.split("/syllabi/")[1].split('.htm')[0] for c in courses_url]

        def convert_ects_str(ects_str: str):
            if ects_str == '':
                return None
            return float(ects_str) if '.' in ects_str else int(ects_str)
        ects = response.xpath("//tr[contains(@class, 'opo_row')]//td[@class='sp']/text()").getall()
        ects = [convert_ects_str(e.split(" ")[0]) for e in ects]

        # Get list of unique courses and ects
        courses, courses_url, ects = zip(*set(zip(courses, courses_url, ects)))

        yield {
            'id': program_id,
            'name': program_name,
            'cycle': cycle,
            'faculties': [faculty],
            'campuses': [campus],
            'url': response.url,
            'courses': courses,
            'ects': ects,
            'courses_urls': courses_url
        }
