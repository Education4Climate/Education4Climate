# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR

BASE_URL = "https://www.ichec.be/fr/programmes"


class ICHECProgramSpider(scrapy.Spider, ABC):
    """
    Program crawler for ICHEC Brussel Management School
    """

    name = "ichec-programs"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/ichec_programs_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):
        links = response.xpath("//div[@class='formation-link']/a/@href").getall()
        for link in links:
            yield response.follow(link, self.parse_program)

    @staticmethod
    def parse_program(response):
        program_name = response.xpath("//div[@class='formation-title']//h1/text()").get()
        cycle = response.xpath("//div[@class='formation-banner-info-item'][1]/text()[2]").get().strip(" \n")
        ue_ids = response.xpath("//div[@class='formation-tab-content structure']"
                                "//table//a[@class='modal-link']/text()").getall()
        ue_ects = response.xpath("//div[@class='formation-tab-content structure']//table//td[5]/text()").getall()
        yield {"name": program_name,
               "id": "",  # no id it seems
               "faculty": "",  # only one faculty?
               "cycle": cycle,
               "courses": ue_ids,
               "ects": ue_ects}
