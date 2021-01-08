# -*- coding: utf-8 -*-
import scrapy
from abc import ABC

from config.settings import YEAR
BASE_URL = "https://web.umons.ac.be/fr/enseignement/loffre-de-formation-de-lumons/"

class UmonsProgramsSpider(scrapy.Spider, ABC):
    name = "umons-programs"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/umons_programs_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_offer)

    def parse_offer(self, response):
        formations = response.xpath('//span//a[not(contains(@href, "png"))]')
        urls = formations.xpath('@href').getall()
        cycles = formations.xpath('text()').getall()
        assert len(urls) == len(cycles)
        for cycle, url in zip(cycles, urls):
            yield response.follow(url, self.parse_prog, cb_kwargs={'cycle':cycle})

    def parse_details(self, response, cycle):
        programs = response.xpath(
            '//article[starts-with(@class,"shortcode-training training-small scheme-")]/a/@href').getall()
        for program in programs:
            yield response.follow(program, self.parse_prog, cb_kwargs={'cycle':cycle})

    def parse_prog(self, response, cycle):
        href = response.xpath(
            '//a[contains(@class, "button-primary-alt scheme-background scheme-background-hover")]/@href').get()
        if not href:
            yield response.follow(response.url, self.parse_details, cb_kwargs={'cycle':cycle})
        else:
            location = response.xpath(
                '//div[div/text()="Lieu"]').css('div.value::text').get()
            ects = response.xpath(
                '//div[div/text()="Crédits ECTS"]').css('div.value::text').get()
            yield response.follow(url=href, callback=self.parse_prog_detail, cb_kwargs={'location': location, 'ects': ects, 'cycle':cycle})

    @staticmethod
    def parse_prog_detail(response, location, ects, cycle):
        faculty = response.css('td.facTitle::text').get()
        program_name = response.css('td.cursusTitle::text').get()

        courses = response.css('a.linkue::attr(href)').getall()
        program_dict = {'faculty': faculty,
                        'name': program_name,
                        'cycle': cycle,
                        'campus': location,
                        'ects': ects,
                        'courses_urls': courses}
        yield program_dict
