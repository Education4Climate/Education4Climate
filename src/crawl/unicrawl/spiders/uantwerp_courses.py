# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from config.settings import YEAR
from config.utils import cleanup

BASE_URL = "https://www.uantwerpen.be/en/study/programmes/all-programmes/{}/study-programme/"
COURSE_URL = "https://www.uantwerpen.be/ajax/courseInfo{}"
PROG_DATA_PATH = Path(f'../../data/crawling-output/uantwerp_programs_{YEAR}.json')
LANGUAGE_DICT = {"Dutch": 'nl',
                 "English": 'en',
                 "French": 'fr'}


class UantwerpCourseSpider(scrapy.Spider, ABC):
    name = "uantwerp-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/uantwerp_courses_{YEAR}.json',
    }

    def start_requests(self):

        programs_codes = set(pd.read_json(open(PROG_DATA_PATH, "r"))["id"].tolist())
        i = 0
        for code in programs_codes:
            # This is used to take into account programs with options (e.g. see Bachelor of Applied Linguistics)
            sub_codes = code.split(" ")
            url = BASE_URL.format(sub_codes[0])
            if len(sub_codes) == 2:
                url += sub_codes[1] + "/"

            yield scrapy.Request(url=url, callback=self.parse_courses)

            if i == 5:
                return
            i += 1

    def parse_courses(self, response):

        main_panel = f"//section[contains(@id, '-{YEAR}')]//section[@class='course']"
        # One course can be several times in the same program
        courses_names = response.xpath(f"{main_panel}/header/h5/a/text()").getall()
        courses_links = response.xpath(f"{main_panel}/header/h5/a/@href").getall()
        for course_name, course_link in list(set(zip(courses_names, courses_links))):
            course_info_panel = f"{main_panel}/header[h5/a[text()=\"{course_name}\"]][1]/following::div[1]"
            course_id = response.xpath(f"{course_info_panel}//div[contains(@class, 'guideNr')]"
                                       f"//div[@class='value']/text()").get().replace('\n', '').replace('\t', '')
            # TODO: check if there can be several languages
            languages = response.xpath(f"{course_info_panel}//div[contains(@class, 'language')]"
                                       f"//div[@class='value']/text()").getall()
            languages = list(set([LANGUAGE_DICT[language.replace('\n', '').replace('\t', '')]
                                  for language in languages]))

            teachers = list(set(response.xpath(f"{course_info_panel}//div[contains(@class, 'teachers')]"
                                               f"//div[@class='value']//a/text()").getall()))

            base_dict = {"id": course_id,
                         "name": course_name,
                         "year": f"{YEAR}-{int(YEAR)+1}",
                         "language": languages,
                         "teachers": teachers}

            yield response.follow(COURSE_URL.format(course_link), self.parse_course, cb_kwargs={"base_dict": base_dict})
            return
        return

    @staticmethod
    def parse_course(response, base_dict):

        content = cleanup(response.xpath("//section[contains(header/h3/a/text(), 'Learning outcomes')]/div").get())
        content += "\n" + cleanup(response.xpath("//section[contains(header/h3/a/text(),"
                                                 " 'Course contents')]/div").get())
        base_dict["url"] = response.url
        base_dict["content"] = content
        yield base_dict
