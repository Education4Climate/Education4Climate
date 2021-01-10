# -*- coding: utf-8 -*-
import scrapy
from abc import ABC
import re

from config.settings import YEAR
BASE_URL = "https://www.usaintlouis.be/sl/enseignement_prog2020.html"

class UslbProgramsSpider(scrapy.Spider, ABC):
    name = "uslb-programs"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/uslb_programs_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_offer)

    def parse_offer(self, response):
        bachelor_faculties = response.css('p.p5').css('a::attr(href)').getall()
        # masters = 
        for fac in bachelor_faculties:
            yield response.follow(fac, self.parse_prog, cb_kwargs={'cycle':'BA'})

    def parse_details(self, response, cycle):
        pass

    def parse_prog(self, response, cycle):
        # https://www.usaintlouis.be/sl/2020/filo1ba.html
        block = response.xpath('//p[(((count(preceding-sibling::*) + 1) = 5) and parent::*)]').get()
        ects = re.split(" crédits", block)[0][-3:]
        courses_url = response.css('div.item_c40').css('a::attr(href)').getall()[1]
        yield response.follow(url=courses_url, callback=self.parse_prog_detail, cb_kwargs={'ects': ects, 'cycle': cycle})


    @staticmethod
    def parse_prog_detail(response, ects, cycle):
        # https://www.usaintlouis.be/sl/2020/prog_filo1ba.html
        program_name = response.css('p.ProgrammeTitre::text').get()
        courses_urls = response.css('a.coursplan::attr(href)').getall()
        program_dict = {'cycle': cycle,
                        'name': program_name,
                        # 'campus': ,
                        'ects': ects,
                        'courses_urls': courses_urls}
        yield program_dict
