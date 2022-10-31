# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://bamaflexweb.hogent.be/BMFUIDetailxOLOD.aspx?a={}&b=5&c=1"  # format brackets will hold code course
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}hogent_programs_{YEAR}.json')

LANGUAGES_DICT = {
    "Frans": 'fr',
    "Engels": 'en',
    "Nederlands": 'nl',
    "Spaans": "es",
    "Duits": "de",
    "Chinees": "cn",
    "Mandarijn Chinees": "cn"
}


class HOGENTCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for HOGENT
    """

    name = "hogent-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}hogent_courses_{YEAR}.json')
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        fn = '/home/duboisa1/shifters/Education4Climate/data/crawling-output/hogent_courses_2022_part1.json'
        a = pd.read_json(fn, orient='records')['id'].to_list()

        for course_id in courses_ids_list:

            if course_id in a:
                print(course_id)
                continue

            yield scrapy.Request(
                url=BASE_URL.format(course_id),
                callback=self.parse_course,
                cb_kwargs={"course_id": course_id},
            )

    @staticmethod
    def parse_course(response, course_id):

        body = response.css("#content")
        name = body.css("h2::text").get()
        year = body.css("#ctl00_ctl00_cphGeneral_cphMain_lblAcademiejaarOmschrijving::text").get()

        teachers = body.xpath("//span[text()='Coördinator: ' or text()='Docenten: ' "
                              "or text()='Andere docenten: ']/following::span[1]/text()").getall()
        teachers = ",".join(teachers).strip(", ")
        teachers = [t.strip() for t in teachers.split(",")] if teachers else []

        languages = body.xpath("//span[text()='Onderwijstalen: ']/following::span[1]/text()").get()
        print(languages)
        if languages:
            languages = [lang.strip() for lang in languages.split(',')]
            languages = [lang for lang in languages if lang != 'Taaloverschrijdend']
            languages = [LANGUAGES_DICT[lang] if lang in LANGUAGES_DICT else 'other' for lang in languages]
            languages = ["nl"] if len(languages) == 0 else languages
        else:
            languages = ['nl']
        print(languages)

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
