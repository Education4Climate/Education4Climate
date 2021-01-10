# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import scrapy
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from config.settings import YEAR
from config.utils import cleanup

PROG_DATA_PATH = Path(f'../../data/crawling-output/uslb_programs_{YEAR}.json')

class UslbCoursesSpider(scrapy.Spider):
    name = "uslb-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/uslb_courses_{YEAR}.json',
    }

    def start_requests(self):
        courses_urls = pd.read_json(open(PROG_DATA_PATH, "r"))["courses_urls"]
        courses_urls_list = sorted(list(set(courses_urls.sum())))
        
        for course_url in courses_urls_list:
            yield scrapy.Request(url=course_url, callback=self.parse_course)

    @staticmethod
    def parse_course(response):
    # https://www.usaintlouis.be/sl/2020/CHIST1111.html

        title = response.css('p.ProgrammeTitre::text').get().strip()
        course_id = title.split(' - ')[0]
        course_name = title.split(' - ')[1]
        yield {
            'name': course_name,
            'id': course_id,
            # 'year': years,
            # 'teacher': teachers,
            # 'language': languages,
            # 'content': content,
            'url': response.url,
        }
