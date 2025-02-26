# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://bamaflexweb.ehb.be/BMFUIDetailxOLOD.aspx?a={}&b=5&c=1"  # format brackets will hold code course
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}ehb_programs_{YEAR}.json')

LANGUAGES_DICT = {
    "Frans": 'fr', 
    "Engels": 'en', 
    "Nederlands": 'nl', 
    "Spaans": "es", 
    "Chinees": "cn",
    "Duits": "de",
    "Mandarijn Chinees": "cn"
}


class EHBCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for Erasmus Hogeschool Brussels
    """

    name = "ehb-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ehb_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(
                url=BASE_URL.format(course_id),
                callback=self.parse_course, 
                cb_kwargs={"course_id": course_id},
            )

    @staticmethod
    def parse_course(response, course_id):

        body = response.css("#content")
        name = body.css("h2::text").get()
        if name:
            name = name.split(" - ")[-1]
        year = body.css("#ctl00_ctl00_cphGeneral_cphMain_lblAcademiejaarOmschrijving::text").get()

        teachers = body.xpath("//span[text()='Coördinator: ' or text()='Docenten: ' or text()='Andere docenten: ']/following::span[1]/text()").getall()
        teachers = ",".join(teachers).strip(", ") 
        teachers = [t.strip().title() for t in teachers.split(",")] if teachers else []

        languages = body.xpath("//span[text()='Onderwijstalen: ']/following::span[1]/text()").get()
        languages = [LANGUAGES_DICT[lang.strip()] for lang in languages.split(',')] if languages else ["nl"]
        languages = ["nl"] if len(languages) == 0 else languages

        content = cleanup(body.xpath("//h4[contains(text(),'Inhoud')]/following::div[1]").xpath("string(.)").get())

        yield {
            'id': course_id,
            'name': name,
            'year': year,
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            'content': content,
            'goal': '',
            'activity': '',
            'other': ''
        }
