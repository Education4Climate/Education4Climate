# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR

# TODO: Done in English because the structure from there is strangely more simplified than in Netherlands
#   Still a bit afraid that there will be more missing information here...
BASE_URL = "https://www.uantwerpen.be/en/study/education-and-training/"


class UantwerpProgramSpider(scrapy.Spider, ABC):
    name = "uantwerp-programs"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/uantwerp_programs_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_main)

    def parse_main(self, response):
        program_links = response.xpath("//section[contains(@class, 'courseItem')]/a/@href").getall()
        i = 0
        for href in program_links:
            yield response.follow(href, self.parse_program_info)
            i += 1
            if i == 10:
                return

    def parse_program_info(self, response):
        name = response.xpath("//span[@class='main']/text()").get()
        if "(Discontinued)" in name:
            return
        faculty = response.xpath("//div[contains(@class, 'managedContent')]//li[2]/a/text()").get()
        campus = response.xpath("//div[contains(@class, 'managedContent')]//li[3]/a/text()").get()
        base_dict = {'id': response.url.split("/")[-2],  # didn't find any id for programs so using url
                     'name': name,
                     'faculty': faculty,
                     'campus': campus}
        yield response.follow(response.url + "study-programme/",
                              self.parse_study_program,
                              cb_kwargs={"base_dict": base_dict})

    def parse_study_program(self, response, base_dict):

        # Check if there are sub-programs. If so, click on the link and call the function recursively.
        subprograms_links = response.xpath("//nav[@class='navSub']//li/a/@href").getall()
        if len(subprograms_links) != 0:
            for link in subprograms_links:
                cur_dict = base_dict.copy()
                cur_dict["id"] += " " + link.split("/")[-2]
                yield response.follow(link, self.parse_study_program, cb_kwargs={"base_dict": cur_dict})
            return

        main_tab = f"//section[contains(@id, '-{YEAR}')]"
        courses_links = response.xpath(f"{main_tab}//h5//a/@href").getall()
        courses_codes = [link.split("-")[1].split("&")[0] for link in courses_links]
        ects = response.xpath(f"{main_tab}//div[@class='spec points']/div[@class='value']/text()").getall()
        ects = [e.split(" ")[0].replace('\n', '').replace('\t', '') for e in ects]

        # One course can be several times in the same program
        courses_codes, ects = zip(*list(set(zip(courses_codes, ects))))

        cur_dict = {"courses": courses_codes,
                    "ects": ects}

        yield {**base_dict, **cur_dict}
