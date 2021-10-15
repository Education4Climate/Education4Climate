# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy
import re
from difflib import get_close_matches as close_matches

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL_1 = "https://www.howest.be/nl"
BASE_URL_2 = "https://app.howest.be/bamaflex/ectssearch.aspx"

acad_year = "{}".format(YEAR)

BASE_POST_DATA = {
    "dropdownlistLanguage": "1",
    "dropdownlistAcademiejaar": "{}-{}".format(acad_year, int(acad_year[-2:])+1),
    "hiddenAfstudeerrichtingCode": "",
}


class HOWESTProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for Hogeschool West-Vlaanderen 

    METHOD:
    Information about programs at HOWEST are scattered between two sites.
    The first one (https://www.howest.be/nl) provides the names, campuses, 
    cycles, faculties and a description of programs. 
    The second one (https://app.howest.be/bamaflex/ectssearch.aspx) provides 
    the lists of courses (and ects) for each program.
    The data from each site is merged based on the name of the program. 
    Unfortunately, there are slight differences in program names across sites.
    For each program on the first site, we try to find the closest match on the second site
    using the 'difflib' package. Matches have been manually checked for 2020-21.
    If no match is found, the program is not crawled.
    """

    name = "howest-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}howest_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(
            url=BASE_URL_1,
            callback=self.parse_home_page
        )

    def parse_home_page(self, response):
        programs_urls = response.css(".subgroup > .item-list > ul > li > a::attr(href)").getall()
        yield from response.follow_all(programs_urls, callback=self.parse_program_info)

    def parse_program_info(self, response):

        name = response.css("h1::text").get()
        sub_title = response.css("page-sub-title a::text").get()
        campuses = response.css(".oplfiche").xpath("div/strong[text()='Locatie:']/following::ul[1]/li/text()").getall()
        faculty = response.css(".oplfiche").xpath("div[strong[text()='Studiedomein:']]/a/text()").get()

        cycle = response.css(".oplfiche").xpath("div[strong[text()='Diploma:']]/a/text()").get()
        if not cycle:
            cycle = response.css(".oplfiche").xpath("div[strong[text()='Diploma:']]/text()").get()

        if cycle is not None:
            if "Bachelor" in cycle:
                cycle = 'bac'
            elif "Master" in cycle:
                cycle = 'master'
            elif 'Graduaat' in cycle:
                cycle = 'grad'
        else:
            cycle = "other"

        base_dict = {
            "id": '',  # id is added in the next section
            "name": sub_title if sub_title else name,
            "cycle": cycle,
            "faculties": [faculty],
            "campuses": campuses,
            # "ects" : [] # ECTS are extracted at the course level
            "url": response.url,
        }

        # METHOD : 
        # The list of courses of each programs is listed on another website
        yield scrapy.Request(
            url=BASE_URL_2,
            callback=self.parse_programs_ids,
            cb_kwargs={"base_dict": base_dict},
            dont_filter=True
        )

    def parse_programs_ids(self, response, base_dict):
        programs = response.css("#dropdownlistOpleidingen option::text").getall()
        programs_ids = response.css("#dropdownlistOpleidingen option::attr(value)").getall()

        # METHOD :
        # The titles of the programs are slightly different on both sites.
        # Find the closest match. Only the first match is kept.
        # This method is not perfect. Some matches are not found (only one in my tests).
        # Other programs have multiple valid matches, but only the first one is used.
        name = close_matches(base_dict["name"], programs)

        if name:
            prog_index = programs.index(name[0])
            prog_id = programs_ids[prog_index]

            post_data = BASE_POST_DATA.copy()
            post_data['dropdownlistOpleidingen'] = prog_id
            
            base_dict["id"] = prog_id

            yield scrapy.http.FormRequest.from_response(
                    response,
                    callback=self.parse_program_courses,
                    formdata=post_data,
                    dont_click=True,
                    cb_kwargs={"base_dict": base_dict}
                )

    def parse_program_courses(self, response, base_dict):
        prog_paths_ids = response.css("#dropdownlistTrajecten option::attr(value)").getall()

        # Scrape courses sequentially from every program 'path' and collect them in shared 'base_dict'
        if prog_paths_ids:
            base_dict["courses"] = []
            post_data = BASE_POST_DATA.copy()
            post_data['dropdownlistOpleidingen'] = base_dict["id"]
            post_data["dropdownlistTrajecten"] = prog_paths_ids[0]
            yield scrapy.http.FormRequest.from_response(
                response,
                callback=self.parse_paths_courses_recursively,
                formdata=post_data,
                cb_kwargs={"base_dict": base_dict, "post_data": post_data, "paths_ids": prog_paths_ids[1:]}
            )

    def parse_paths_courses_recursively(self, response, base_dict, post_data, paths_ids):
        courses_urls = response.css("#panelProgramma > ul > li > a::attr(href)").getall()
        # Collect courses ids while avoiding duplicates
        courses_ids = set([re.findall("\?a=(.+)&b", url)[-1] for url in courses_urls])
        base_dict["courses"] = list(set(base_dict["courses"]).union(courses_ids))

        # Parse the next program 'path' or yield final result
        if paths_ids:
            post_data["dropdownlistTrajecten"] = paths_ids[0]
            yield scrapy.http.FormRequest.from_response(
                response,
                callback=self.parse_paths_courses_recursively,
                formdata=post_data,
                cb_kwargs={"base_dict": base_dict, "post_data": post_data, "paths_ids": paths_ids[1:]}
            )
        else:
            if base_dict["courses"]:
                yield base_dict
