# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy
import re
from difflib import get_close_matches as close_matches

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL_1 = "https://www.howest.be/nl/opleidingen?{}&page={}"
BASE_URL_2 = "https://app.howest.be/bamaflex/ectssearch.aspx"

acad_year = "{}".format(YEAR)

BASE_POST_DATA = {
    "dropdownlistLanguage": "1",
    "dropdownlistAcademiejaar": "{}-{}".format(acad_year, int(acad_year[-2:])+1),
    "hiddenAfstudeerrichtingCode": "",
    "sm1": "updatePanelMain|buttonZoek",
    "buttonZoek": "Zoeken",
    "__EVENTTARGET": '',
    "__EVENTARGUMENT": '',
    "__LASTFOCUS": '',
    "__ASYNCPOST": 'true'
}

FACULTIES_CODE = {
    "Architectuur, Energie & Bouw": "f%5B0%5D=interesse%3A10",
    "Business & Ondernemen": "f%5B0%5D=interesse%3A11",
    "Gezondheid & Zorg": "f%5B0%5D=interesse%3A13",
    "Media & Communicatie": "f%5B0%5D=interesse%3A14",
    "Mens & Samenleving": "f%5B0%5D=interesse%3A15",
    "Onderwijs": "f%5B0%5D=interesse%3A16",
    "Productontwerp, Digital Design & Arts": "f%5B0%5D=interesse%3A12",
    "Sport, Toerisme & Recreatie": "f%5B0%5D=interesse%3A17",
    "Tech & IT": "f%5B0%5D=interesse%3A18"
}


class HOWESTProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Hogeschool West-Vlaanderen
    """

    name = "howest-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}howest_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        for fac_name, fac_code in FACULTIES_CODE.items():
            for i in range(8):   # CHECK the max number of programs per faculty / 10
                yield scrapy.Request(
                    url=BASE_URL_1.format(fac_code, i),
                    callback=self.parse_home_page,
                    cb_kwargs={'faculty': fac_name}
                )

    def parse_home_page(self, response, faculty):
        programs_urls = response.xpath("//h3/a/@href").getall()
        for url in programs_urls:
            yield response.follow(url + "#opleidingsprogramma", callback=self.parse_program,
                                  cb_kwargs={'faculty': faculty})

    def parse_program(self, response, faculty):

        program_content_link = response.xpath("//*[@id='opleidingsprogramma']/a/@href").get()
        # Some programs do not have a list of courses associated
        if program_content_link:

            campus = response.xpath('//*[@id="headercontent"]/div/div/div[1]/span[1]/span/span/a/text()').get()
            campus = campus.split(" – ")[0]

            yield response.follow(program_content_link, callback=self.parse_content,
                                  cb_kwargs={'faculty': faculty, 'campus': campus})

    def parse_content(self, response, faculty, campus):

        # Get all data for the post
        post_data = BASE_POST_DATA.copy()
        program_id = response.xpath('//*[@id="dropdownlistOpleidingen"]/option[@selected="selected"]/@value').get()
        post_data['dropdownlistOpleidingen'] = program_id
        post_data['__VIEWSTATE'] = response.xpath("//input[@id='__VIEWSTATE']/@value").get()
        post_data['__VIEWSTATEGENERATOR'] = response.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value").get()
        post_data['__EVENTVALIDATION'] = response.xpath("//input[@id='__EVENTVALIDATION']/@value").get()

        traject_ids = response.xpath('//*[@id="dropdownlistTrajecten"]/option/@value').getall()

        program_name = response.xpath('//*[@id="dropdownlistOpleidingen"]/option[@selected="selected"]/text()').get()
        program_name = program_name.split(" -")[0]
        cycle = 'other'
        if "bachelor" in program_name.lower():
            cycle = 'bac'
        elif "master" in program_name.lower():
            cycle = 'master'
        elif 'postgraduaat' in program_name.lower():
            cycle = 'postgrad'
        elif 'graduaat' in program_name.lower():
            cycle = 'grad'

        base_dict = {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculties": [faculty],
            "campuses": [campus],
            "url": response.url,
            # "ects": ects are obtained at course level
            "courses": []
        }

        # Call recursively on each trajectory
        post_data["dropdownlistTrajecten"] = traject_ids[0]
        yield scrapy.http.FormRequest(
            response.url,
            callback=self.parse_paths_courses_recursively,
            formdata=post_data,
            cb_kwargs={"base_dict": base_dict, "post_data": post_data, "traject_ids": traject_ids[1:]}
        )

    def parse_paths_courses_recursively(self, response, base_dict, post_data, traject_ids):

        courses = response.xpath('//*[contains(@id, "repeaterModules_hyperlinkModule")]/@href').getall()
        courses_urls = [course.split("aspx?")[1] for course in courses]
        courses_ids = [course.split("a=")[1].split('&b')[0] for course in courses_urls]
        base_dict["courses"] = list(set(base_dict["courses"]).union(courses_ids))

        # Parse the next program 'path' or yield final result
        if traject_ids:
            post_data["dropdownlistTrajecten"] = traject_ids[0]
            yield scrapy.http.FormRequest(
                response.url,
                callback=self.parse_paths_courses_recursively,
                formdata=post_data,
                cb_kwargs={"base_dict": base_dict, "post_data": post_data, "traject_ids": traject_ids[1:]}
            )
        else:
            # Do not save programs without courses --> TODO: should we ?
            if base_dict["courses"]:
                yield base_dict
