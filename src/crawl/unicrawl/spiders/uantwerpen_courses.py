# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

COURSE_URL = "https://www.uantwerpen.be/ajax/courseInfo{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}uantwerpen_programs_{YEAR}.json')
LANGUAGE_DICT = {
    "Dutch": 'nl',
    "Nederlands": 'nl',
    "English": 'en',
    "Engels": 'en',
    "French": 'fr',
    "Frans": 'fr',
    "Duits": 'de',
    "Spaans": 'es',
    "Italiaans": 'it',
    "Chinees": 'cn',
    "German": 'de',
    "Spanish": 'es'
}

# WARNING: don't forget to uncomment the line 'HTTPERROR_ALLOWED_CODES = ['404']' in settings.py


class UAntwerpenCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for UAntwerpen
    """

    name = "uantwerpen-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}uantwerpen_courses_{YEAR}_pre.json').as_uri()
    }

    def start_requests(self):

        study_programs_url = set(pd.read_json(open(PROG_DATA_PATH, "r"))["url"].tolist())
        for url in study_programs_url:
            yield scrapy.Request(url=url, callback=self.parse_courses)

    def parse_courses(self, response):

        main_panel = f"//section[contains(@id, '-{YEAR}')]//section[@class='course']"
        # One course can be several times in the same program
        courses_names = response.xpath(f"{main_panel}/header/h5/a/text()").getall()
        courses_links = response.xpath(f"{main_panel}/header/h5/a/@href").getall()
        for course_name, course_link in list(set(zip(courses_names, courses_links))):

            course_id = course_link.split(f'{YEAR}-')[1].split("&")[0]

            course_info_panel = f"{main_panel}/header[h5/a[text()=\"{course_name}\"]][1]/following::div[1]"
            languages = response.xpath(f"{course_info_panel}//div[contains(@class, 'language')]"
                                       f"//div[@class='value']/text()").getall()
            languages = list(set([LANGUAGE_DICT[language.replace('\n', '').replace('\t', '')]
                                  for language in languages]))

            teachers = list(set(response.xpath(f"{course_info_panel}//div[contains(@class, 'teachers')]"
                                               f"//div[@class='value']//a/text()").getall()))
            # Put surname first
            teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]

            base_dict = {
                "id": course_id,
                "name": course_name,
                "year": f"{YEAR}-{int(YEAR)+1}",
                "languages": languages,
                "teachers": teachers
            }

            yield response.follow(COURSE_URL.format(course_link), self.parse_course, cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_course(response, base_dict):

        # Course description
        def get_sections_text(sections_names):
            texts = [cleanup(response.xpath(f"//details[contains(summary/h3/text(),"
                                            f" \"{section}\")]/div").get())
                     for section in sections_names]
            return "\n".join(texts).strip("\n")

        # WARNING: don't forget to uncomment the line 'HTTPERROR_ALLOWED_CODES = ['404']' in settings.py
        if response.status == '404':
            contents = ''
            goals = ''
        else:
            contents = get_sections_text(["Course contents", "Inhoud"])
            goals = get_sections_text(["Learning outcomes", "Eindcompetenties"])

        base_dict["url"] = response.url
        base_dict["content"] = contents
        base_dict["goal"] = goals
        base_dict["activity"] = ''
        base_dict["other"] = ''
        yield base_dict
