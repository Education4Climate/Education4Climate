# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from config.settings import YEAR
from config.utils import cleanup

BASE_URL = "http://applications.umons.ac.be/web/fr/pde/2020-2021/ue/{}.htm"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../data/crawling-output/umons_programs_{YEAR}.json')

LANGUAGE_DICT = {"Français": "fr",
                 "Anglais": "en",
                 "Néerlandais": "nl",
                 "Allemand": "de",
                 "Espagnol": "es",
                 "Danois": "dk",
                 "Italien": "it",
                 "Russe": "ru",
                 "Arabe": "ar",
                 "Chinois": "cn",
                 "Japonais": "jp",
                 "Norvégien": "no",
                 "Polonais": "po",
                 "Portugais": "pt",
                 "Suédois": "se"
                 }


class UmonsCourseSpider(scrapy.Spider, ABC):
    name = "umons-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../data/crawling-output/umons_courses_{YEAR}.json')
    }

    def start_requests(self):
        courses = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_list = sorted(list(set(courses.sum())))

        for course in courses_list:
            base_dict = {"id": course}
            yield scrapy.Request(url=BASE_URL.format(course),
                                 callback=self.parse_course,
                                 cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_course(response, base_dict):

        course_name = response.css("td.UETitle::text").get()
        year = response.css('td.toptile::text').get().split(' ')[2]

        main_teacher = response.xpath("//table[@class='UETbl'][1]//td[3]//text()").get()
        teachers = list(set([main_teacher] + response.xpath("//table[@class='UETbl'][1]//td[5]//li/text()").getall()))

        languages = response.xpath("//table[@class='UETbl'][2]//td[1]//li/text()").getall()
        languages_codes = []
        for languages_list in languages:
            languages_codes += \
                [LANGUAGE_DICT[l.replace(" niveau 1", '').replace(" niveau 2", '').replace(" niveau 3", '')]
                 for l in languages_list.split(', ')]

        goal = cleanup(response.xpath(f"//div[p/text()="
                                      f"\"Objectifs par rapport aux acquis d'apprentissage du programme\"]/ul").get())
        sections = ["Acquis d'apprentissage UE", "Contenu de l'UE"]
        contents = [cleanup(response.xpath(f"//div[p/text()=\"{section}\"]/p[@class='texteRubrique']").get())
                    for section in sections]
        content = goal + "\n" + "\n".join(contents)
        content = '' if content == "\n\n" else content

        cur_dict = {
            'name':  course_name,
            'year':  year,
            'teacher': teachers,
            'language': languages_codes,
            'url': response.url,
            'content': content
        }
        yield {**base_dict, **cur_dict}
