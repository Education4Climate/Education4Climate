from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'https://caliweb.vub.be/'

# Note: need to change the parameter ROBOTS_OBEY in the crawler settings.py to make the crawler work


class VUBProgramSpider(scrapy.Spider, ABC):
    name = "vub-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}vub_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_main)

    def parse_main(self, response):

        program_links = response.xpath("//i/a/@href").getall()[2:-5]
        for link in program_links:
            yield response.follow(link, self.parse_second)

    def parse_second(self, response):
        traject_links = response.xpath("//i/a/@href").getall()
        for link in traject_links:
            yield response.follow(link, self.parse_program)
            return

    @staticmethod
    def parse_program(response):

        main_program_id = response.url.split("id=")[1].split("&")[0]
        sub_program_id = response.url.split("anchor=")[1].split("&")[0]

        program_name = response.xpath("//h1/text()").get()

        cycle = "other"
        if "Bachelor" in program_name:
            cycle = "bac"
        elif "Postgraduaat" in program_name or "Postgraduate" in program_name:
            cycle = 'postgrad'
        elif "Schakelprogramma Master" in program_name or "Voorbereidingsprogramma Master" in program_name \
                or 'Educatieve master' in program_name:
            cycle = "other"
        elif 'Master' in program_name:
            cycle = "master"

        # Can have multiple faculties
        faculties = response.xpath("//p[1]/text()").getall()
        faculties = [faculty.strip(".") for faculty in faculties]

        courses_links = response.xpath("//i/a/@href").getall()
        if len(courses_links) == 0:
            return
        courses_codes = [link.split("id=")[1].split("&")[0] for link in courses_links]
        courses_texts = response.xpath("//i/a/text()").getall()
        courses_ects = [int(text.split("ECTS")[0]) for text in courses_texts]

        yield {
            "id": main_program_id + '-' + sub_program_id,  # don't think there are ids, so took one from url
            "name": program_name,
            "cycle": cycle,
            "faculties": faculties,
            "campuses": [],  # didn't find information on campuses
            "url": response.url,
            "courses": courses_codes,
            "ects": courses_ects
        }
