# -*- coding: utf-8 -*-
import scrapy
from abc import ABC
from pathlib import Path

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER
BASE_URL = "https://web.umons.ac.be/fr/enseignement/loffre-de-formation-de-lumons/"


class UMonsProgramSpider(scrapy.Spider, ABC):
    name = "umons-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}umons_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_offer)

    def parse_offer(self, response):
        formations = response.xpath('//span//a[not(contains(@href, "png"))]')
        urls = formations.xpath('@href').getall()
        cycles = formations.xpath('text()').getall()
        assert len(urls) == len(cycles)
        for cycle, url in zip(cycles, urls):
            if 'BA' in cycle:
                cycle = 'bac'
            elif 'MA' in cycle:
                cycle = 'master'
            else:
                cycle = 'other'
            yield response.follow(url, self.parse_prog, cb_kwargs={'cycle': cycle})

    def parse_details(self, response, cycle):

        programs = response.xpath(
            '//article[starts-with(@class,"shortcode-training training-small scheme-")]/a/@href').getall()
        for program in programs:
            yield response.follow(program, self.parse_prog, cb_kwargs={'cycle': cycle})

    def parse_prog(self, response, cycle):

        # Note: this leads to an error on the 'Bachelier en Droit' and 'Bachelier en Sciences Humaines et Sociales'
        #  but anyways these programs are organised by the ULB
        href = response.xpath(
            '//a[contains(@class, "button-primary-alt scheme-background scheme-background-hover")]/@href').get()
        if not href:
            yield response.follow(response.url, self.parse_details, cb_kwargs={'cycle': cycle})
        else:
            campus = response.xpath('//div[div/text()="Lieu"]').css('div.value::text').get()
            yield response.follow(url=href, callback=self.parse_prog_detail,
                                  cb_kwargs={'campus': campus,
                                             'cycle': cycle,
                                             'url': response.url})

    @staticmethod
    def parse_prog_detail(response, campus, cycle, url):

        faculty = response.css('td.facTitle::text').get()
        program_name = response.css('td.cursusTitle::text').get()
        courses = response.css('span.linkcodeue::text').getall()
        courses = [course.strip(" ") for course in courses]
        ects = cleanup(response.xpath("//td[@class='credits colnumber']").getall())
        ects = [int(e) if e != '' else 0 for e in ects]

        yield {
            'id': response.url.split("/")[-1].split(".")[0],
            'name': program_name,
            'cycle': cycle,
            'faculties': [faculty],
            'campuses': [campus],
            'url': url,
            'courses': courses,
            'ects': ects
        }
