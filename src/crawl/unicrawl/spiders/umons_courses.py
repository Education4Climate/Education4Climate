# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import scrapy
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from config.settings import YEAR
from config.utils import cleanup

PROG_DATA_PATH = Path(f'../../data/crawling-output/ucll_programs_{YEAR}.json')

class UmonsCoursesSpider(scrapy.Spider):
    name = "umons-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/umons_courses_{YEAR}.json',
    }

    def start_requests(self):
        courses_urls = pd.read_json(open(PROG_DATA_PATH, "r"))["courses_urls"]
        courses_urls_list = sorted(list(set(courses_urls.sum())))
        
        for course_url in courses_urls_list:
            yield scrapy.Request(url=course_url, callback=self.parse_course)

    @staticmethod
    def parse_course(response):
        first_block = response.css('table.UETbl td::text').getall()

        data = {
            'name':         cleanup(response.css("td.UETitle").get()),
            'id':           cleanup(first_block[0]),
            'year':         cleanup(response.css('td.toptile::text').get().split(' ')[2]),
            'teachers':     cleanup(response.css('table.UETbl')[0].css('li::text').get()),
            'language':     cleanup(response.css('table.UETbl')[1].css('li::text').get()),
            'prerequisite': cleanup(response.xpath('//div[p/text() = "Compétences préalables"]/p[@class="texteRubrique"]').get()),
            'goal':         cleanup(response.xpath('//div[p/text() = "Acquis d\'apprentissage UE"]/p[@class="texteRubrique"]').get()),
            'content':      cleanup(response.xpath('//div[p/text() = "Contenu de l\'UE"]/p[@class="texteRubrique"]').get()),
            'url':          response.url
        }
        yield data
