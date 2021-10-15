# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URl = "https://bamaflexweb.howest.be/bamaflexweb/BMFUIDetailxOLOD.aspx?a={}&b=5&c=1"  # format is code course
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}howest_programs_{YEAR}.json')

LANGUAGES_DICT = {
    "Frans": 'fr', 
    "Engels": 'en', 
    "Nederlands": 'nl', 
    "Spaans": "es", 
    "Chinees": "cn",
    "Duits": "de",
    "Mandarijn Chinees": "cn",
}


class HOWESTCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Hogeschool West-Vlaanderen
    """

    name = "howest-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}howest_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            base_dict = {"id": course_id}

            yield scrapy.Request(
                url=BASE_URl.format(course_id), 
                callback=self.parse_course, 
                cb_kwargs={"base_dict": base_dict},
            )

    @staticmethod
    def parse_course(response, base_dict):

        body = response.css("#content")
        name = body.css("h2::text").get()
        year = body.css("#ctl00_ctl00_cphGeneral_cphMain_lblAcademiejaarOmschrijving::text").get()
        ects = body.css("#ctl00_ctl00_cphGeneral_cphMain_lblInhoudStudieomvang::text").get()
        ects = int(ects.split("\xa0")[0]) if ects else ""

        teachers = body.xpath("//span[text()='Coördinator: ' or text()='Docenten: ' or text()='Andere docenten: ']"
                              "/following::span[1]/text()").getall()
        teachers = ",".join(teachers).strip(", ") 
        teachers = [t.strip() for t in teachers.split(",")] if teachers else []

        languages = body.xpath("//span[text()='Onderwijstalen: ']/following::span[1]/text()").get()
        languages = [LANGUAGES_DICT[lang.strip()] for lang in languages.split(',')] if languages else ["nl"]

        content = cleanup(body.xpath("//h4[contains(text(),'Inhoud')]/following::div[1]").xpath("string(.)").get())

        yield {
            'id': base_dict['id'],
            'name': name,
            'year': year,
            'ects': ects, # TODO: does not work in prepare.py
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            'content': content,
            'goal': '',
            'activity': '',
            'other': ''
        }
