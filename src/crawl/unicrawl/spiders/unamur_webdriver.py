# -*- coding: utf-8 -*-

import os
import time

import numpy as np
import pandas as pd

from src.crawl.config.driver import Driver
import scrapy
from scrapy.crawler import CrawlerProcess


import config.utils as u
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

    @staticmethod
    def parse(response):
        codes = u.cleanup(response.xpath("//tr//td[@class='code']").getall())
        links = u.cleanup(response.xpath("//tr//td[@class='name']/a/@href").getall())
        for code, link in zip(codes, links):
            yield {'code': code, 'url': link}


class UNamurCourseSpider(scrapy.Spider):
    name = "unamur-course"

    def __init__(self, *args, **kwargs):
        self.myurls = kwargs.get('myurls', [])
        super(UNamurCourseSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.myurls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        name_and_id = u.cleanup(response.css("h1::text").get())
        name = name_and_id.split("[")[0]
        id = name_and_id.split("[")[1].strip("]")

        years = u.cleanup(response.xpath("//div[@class='foretitle']").get()).strip("Cours ")
        # TODO: do we keep the 'suppléant'?
        teachers = u.cleanup(response.xpath("//div[contains(text(), 'Enseignant')]/a").getall())

        # TODO: cours en plusieurs langues?
        languages = u.cleanup(response.xpath("//div[contains(text(), 'Langue')]").getall())
        languages = [lang.split(": ")[1] for lang in languages]
        # TODO: check all langagae used
        languages_code = {"Français": 'fr',
                          "Anglais / English": 'en',
                          "Allemand / Deutsch": 'de',
                          "Néerlandais / Nederlands": 'nl',
                          "Italien": "it",
                          "Espagnol / Español": "es"}
        languages = [languages_code[lang] for lang in languages]


        # TODO: too much content selected?
        content = u.cleanup(response.xpath("//div[@class='tab-content']").get())

        cycle_ects = u.cleanup(response.xpath("//div[@id='tab-studies']/table/tbody//td").getall())
        cycles = []
        ects = []
        programs = []
        for i, el in enumerate(cycle_ects):
            if i % 3 == 0:
                programs += [el]
                if "Bachelier" in el:
                    cycles += ["bachelier"]
                elif "Master" in el:
                    cycles += ["Master"]
                else:
                    cycles += [el]
            elif i % 3 == 2:
                ects += [int(el)]

        # TODO: need to check if there are not sometimes several campuses or faculties
        organisation = response.xpath("//div[@id='tab-practical-organisation']").get()
        campus = ''
        if "Lieu de l'activité" in organisation:
            campus = u.cleanup(organisation.split("Lieu de l'activité")[1].split("Faculté organisatrice")[0])
        faculty = u.cleanup(organisation.split("Faculté organisatrice")[1].split("<br>")[0])

        data = {
            'name': name,
            'id': id,
            'year': years,
            'teacher': teachers,
            'language': languages,
            'cycle': cycles,
            'ects': ects,
            'content': content,
            'url': response.url,
            'faculty': faculty,
            'campus': campus,
            'program': programs
        }
        yield data


def get_programs_and_courses(output):

    # Get list of programs using selenium
    programs_df = get_programs()
    print("Obtained list of programs.")

    # Get list of course using scrappy
    if os.path.exists(output):
        os.remove(output)
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': output
    })
    process.crawl(UNamurProgramSpider, myurls=programs_df["url"].to_list())
    process.start()  # the script will block here until the crawling is finished
    print("Obtained list of courses.")


def crawl_courses(output):
    courses_df = pd.read_json(open("../../../../data/crawling-output/unamur_courses.json", "r")).drop_duplicates()

    # Scrap each course using scrappy
    if os.path.exists(output):
        os.remove(output)
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': output
    })
    process.crawl(UNamurCourseSpider, myurls=courses_df["url"].to_list())
    process.start()  # the script will block here until the crawling is finished
    print("Crawled all courses.")


if __name__ == '__main__':

    # TODO: is there a way to execute the two crawlers in the same run?
    if 0:
        output_ = "../data/crawling-output/unamur_courses.json"
        get_programs_and_courses(output_)
    if 1:
        output_ = '../data/crawling-output/unamur_2020.json'
        crawl_courses(output_)
