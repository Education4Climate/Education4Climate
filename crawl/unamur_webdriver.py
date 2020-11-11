# -*- coding: utf-8 -*-

import os
import time

import numpy as np
import pandas as pd

from crawl.driver import Driver
import scrapy
from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags

import re
import json
import progressbar
import settings as s

import sys
sys.path.append(os.getcwd())


def get_programs():

    unamur_driver = Driver()
    unamur_driver.init()

    unamur_driver.driver.get("https://directory.unamur.be/teaching/programmes")
    # Get all faculties
    year = 2020
    faculties = unamur_driver.driver.find_elements_by_xpath(f"//div[@id='tab-{year}']//h3/a")
    for faculty in faculties:
        time.sleep(0.1)
        faculty.click()

    # Get formation types (keep only the ones starting with Bachelier and Master)
    formation_types = unamur_driver.driver.find_elements_by_xpath(f"//div[@id='tab-{year}']//h4/a")
    formation_types = np.array(formation_types)[[f.text.startswith("Bachelier")
                                       or f.text.startswith("Master") for f in formation_types]].tolist()
    for ft in formation_types:
        time.sleep(0.1)
        ft.click()

    # Get all formations
    programs = unamur_driver.driver.find_elements_by_xpath(f"//div[@id='tab-{year}']//div//div//a")
    programs = np.array(programs)[[p.text != "" for p in programs]].tolist()

    programs_df = pd.DataFrame(index=range(len(programs)), columns=["nom", "url"])
    programs_df.nom = [f.text for f in programs]
    programs_df.url = [f.get_attribute('href') for f in programs]

    unamur_driver.delete_driver()

    return programs_df


class UNamurProgramSpider(scrapy.Spider):
    name = "unamur-program"

    def __init__(self, *args, **kwargs):
        self.myurls = kwargs.get('myurls', [])
        super(UNamurProgramSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.myurls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        codes = self._cleanup(response.xpath("//tr//td[@class='code']").getall())
        links = self._cleanup(response.xpath("//tr//td[@class='name']/a/@href").getall())
        for code, link in zip(codes, links):
            yield {'code': code, 'url': link}

    # TODO: put that in the parent class?
    def _cleanup(self, data):
        if data is None:
            return ""
        elif isinstance(data, list):
            result = list()
            for e in data:
                result.append(self._cleanup(e))
            return result
        else:
            return remove_tags(data).strip()


class UNamurCourseSpider(scrapy.Spider):
    name = "unamur-course"

    def __init__(self, *args, **kwargs):
        self.myurls = kwargs.get('myurls', [])
        super(UNamurCourseSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.myurls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        name_and_id = self._cleanup(response.css("h1::text").get())
        name = name_and_id.split("[")[0]
        id = name_and_id.split("[")[1].strip("]")

        years = self._cleanup(response.xpath("//div[@class='foretitle']").get()).strip("Cours ")
        # TODO: do we keep the 'suppléant'?
        teachers = self._cleanup(response.xpath("//div[contains(text(), 'Enseignant')]/a").getall())

        # TODO: cours en plusieurs langues?
        languages = self._cleanup(response.xpath("//div[contains(text(), 'Langue')]").getall())
        languages = [lang.split(": ")[1] for lang in languages]
        # TODO: check all langugaes used
        languages_code = {"Français": 'fr',
                          "Anglais": 'en',
                          "Allemand": 'de',
                          "Néerlandais": 'nl',
                          "Italien": "it",
                          "Espagnol": "es"}
        languages = [languages_code[lang] for lang in languages]

        # TODO: selecting too much --> need to focus on section 'Contenu'
        content = self._cleanup(response.xpath("//div[@class='tab-content']").get())

        # ects and cycle
        # TODO -> need to take it from formation different numbers of credits (see https://directory.unamur.be/teaching/courses/LCLAB101/2020)
        # ects = self._cleanup(response.xpath("//ul[@class='inline list-separator']/li[contains(text(), 'crédit')]").get())
        # ects = int(ects.strip(" crédits"))

        cycle_ects = self._cleanup(response.xpath("//div[@id='tab-studies']/table/tbody//td").getall())
        cycles = []
        ects = []
        for i, el in enumerate(cycle_ects):
            if i % 3 == 0:
                if "Bachelier" in el:
                    cycles += ["bachelier"]
                elif "Master" in el:
                    cycles += ["Master"]
                else:
                    cycles += [el]
            elif i%3 == 2:
                ects += [int(el)]

        data = {
            'name': name,
            'id': id,
            'years': years,
            'teachers': teachers,
            'languages': languages,
            'cycle': cycles,
            'ects': ects,
            'content': content,
            'url': response.url
        }
        yield data

    # TODO: put that in the parent class?
    def _cleanup(self, data):
        if data is None:
            return ""
        elif isinstance(data, list):
            result = list()
            for e in data:
                result.append(self._cleanup(e))
            return result
        else:
            return remove_tags(data).strip()


def main(output):

    # Get list of programs using selenium
    #programs_df = get_programs()

    # Get list of course using scrappy
    if os.path.exists("unamur_courses_list.json"):
        os.remove("unamur_courses_list.json")
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'unamur_courses_list.json'
    })
    myurls = ["https://directory.unamur.be/teaching/programmes/040B/2020"]#, "https://directory.unamur.be/teaching/programmes/050B/2020"]
    process.crawl(UNamurProgramSpider, myurls=myurls) #myurls=programs_df["url"].to_list()[:1])
    #process.start()  # the script will block here until the crawling is finished
    #courses_df = pd.read_json(open("unamur_courses_list.json", "r")).drop_duplicates()

    # Scrap each course using scrappy
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': output
    })
    myurls = ["https://directory.unamur.be/teaching/courses/LCLAB101/2020",
              "https://directory.unamur.be/teaching/courses/LCLAB005/2020",
              "https://directory.unamur.be/teaching/courses/LHISB321/2020"]
    process.crawl(UNamurCourseSpider, myurls=myurls)  # myurls=programs_df["url"].to_list()[:1])
    process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':

    output = 'output.json'
    main(output)
