# -*- coding: utf-8 -*-

import os
from pathlib import Path

import pandas as pd

import scrapy
from scrapy.crawler import CrawlerProcess

from config.settings import YEAR
import config.utils as u

import sys
sys.path.append(os.getcwd())


BASE_URl = "https://directory.unamur.be/teaching/courses/{}/{}" # first format is code course, second is year
PROG_DATA_PATH = Path(f'../../data/crawling-output/unamur_programs_{YEAR}.json')


class UNamurCourseSpider(scrapy.Spider):
    name = "unamur-course"

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URl.format(course_id, YEAR), self.parse)
            exit()

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


def crawl_courses(output):

    # Scrap each course using scrappy
    if os.path.exists(output):
        os.remove(output)
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': output
    })
    process.crawl(UNamurCourseSpider)
    process.start()  # the script will block here until the crawling is finished
    print("Crawled all courses.")


if __name__ == '__main__':

    # output_ = f'../data/crawling-output/unamur_courses_{YEAR}.json'
    output_ = "output.json"
    crawl_courses(output_)
