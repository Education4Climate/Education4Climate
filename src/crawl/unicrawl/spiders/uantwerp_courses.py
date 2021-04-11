# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

COURSE_URL = "https://www.uantwerpen.be/ajax/courseInfo{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}uantwerp_programs_{YEAR}.json')
LANGUAGE_DICT = {"Dutch": 'nl',
                 "Nederlands": 'nl',
                 "English": 'en',
                 "Engels": 'en',
                 "French": 'fr',
                 "Frans": 'fr',
                 "Duits": 'de',
                 "Spaans": 'es'}


class UantwerpCourseSpider(scrapy.Spider, ABC):
    name = "uantwerp-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}uantwerp_courses_{YEAR}_pre.json')
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
            course_info_panel = f"{main_panel}/header[h5/a[text()=\"{course_name}\"]][1]/following::div[1]"
            course_id = response.xpath(f"{course_info_panel}//div[contains(@class, 'guideNr')]"
                                       f"//div[@class='value']/text()").get().replace('\n', '').replace('\t', '')
            languages = response.xpath(f"{course_info_panel}//div[contains(@class, 'language')]"
                                       f"//div[@class='value']/text()").getall()
            languages = list(set([LANGUAGE_DICT[language.replace('\n', '').replace('\t', '')]
                                  for language in languages]))

            teachers = list(set(response.xpath(f"{course_info_panel}//div[contains(@class, 'teachers')]"
                                               f"//div[@class='value']//a/text()").getall()))
            # Put surname first
            teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]

            base_dict = {"id": course_id,
                         "name": course_name,
                         "year": f"{YEAR}-{int(YEAR)+1}",
                         "languages": languages,
                         "teachers": teachers}

            yield response.follow(COURSE_URL.format(course_link), self.parse_course, cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_course(response, base_dict):

        sections = ["Learning outcomes", "Course contents", "Eindcompetenties", "Inhoud"]
        content = ""
        for section in sections:
            section_content = cleanup(response.xpath(f"//section[contains(header/h3/a/text(),"
                                                     f" \"{section}\")]/div").get())
            content += "\n" + section_content if len(section_content) != 0 else ""
        content = content.strip("\n")

        base_dict["url"] = response.url
        base_dict["content"] = content
        yield base_dict
