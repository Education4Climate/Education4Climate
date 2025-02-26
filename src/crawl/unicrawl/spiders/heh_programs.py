from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = f"https://www.heh.be/"


class HEHProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Haute Ecole du Hainaut
    """

    name = 'heh-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}heh_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_programs)

    def parse_programs(self, response):

        # The condition on the 'a' is to avoid the 'covering programs' (e.g. Assistante de direction)
        program_links = response.xpath("//ul[@id='formation_HEH']//ul/li/a[@class='option'"
                                       " or not(contains(text(),':'))]/@href").getall()
        for program_link in program_links:
            print(program_link)
            yield response.follow(
                url=program_link,
                callback=self.parse_program
            )

    @staticmethod
    def parse_program(response):

        program_id = response.url.split('/')[-1]
        program_name = response.xpath("//h1/text()").get()

        cycle = 'bac' if 'Bachelier' in program_name else 'Master'

        faculty = response.xpath("//p[@id='ariane']/a[2]/text()").get()

        courses_urls = response.xpath("//div[contains(@class,'UE')]/a/@href").getall()
        if len(courses_urls) == 0:
            return
        courses_names = response.xpath("//div[a[contains(@class, 'detailCursus_btnECTS')]]/strong/text()").getall()
        courses_ects = response.xpath("//div[contains(@class,'UE')]/strong/span/text()").getall()

        # remove urls which are not generic
        courses_zip = list(zip(courses_urls, courses_names, courses_ects))
        courses_zip = [(url, name, ects) for (url, name, ects) in courses_zip if url.startswith('/upload/ects')]
        courses_urls, courses_names, courses_ects = zip(*courses_zip)

        # Simplify fields
        courses_urls = [url.replace("/upload/ects/", '') for url in courses_urls]
        courses_ects = [int(e.strip('\xa0ECTS)').strip(" (")) for e in courses_ects]

        # Get course ids
        courses_ids = [link.split('-')[-1].split(".")[0] for link in courses_urls]

        if len(courses_names) != len(courses_ids):
            print(response.url)
            print(len(courses_names))
            print(courses_names)
            print(len(courses_ids))
            print(courses_ids)

        yield {
            'id': program_id,
            'name': program_name,
            'cycle': cycle,
            'faculties': [faculty],
            'campuses': [],
            'url': response.url,
            'courses': courses_ids,
            'ects': courses_ects,
            'courses_names': courses_names,
            'courses_urls': courses_urls
        }
