# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = "http://extranet.ihecs.be/?ects=go&act=showfiche&codeue={}" + f"&anneeaca={YEAR}_{YEAR+1}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}ihecs_programs_{YEAR}.json')

LANGUAGES_DICT = {"Français": "fr",
                  "Fr": "fr",
                  "Anglais": "en",
                  "English": "en",
                  "Allemand": "de",
                  "Deutsch": "de",
                  "Néerlandais": "nl",
                  "Nederlands": "nl",
                  "Espagnol": 'es',
                  "Español": 'es',
                  "Italien": 'it',
                  "Italiano": 'it'
                  }


class IHECSCourseSpider(scrapy.Spider, ABC):
    name = "ihecs-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ihecs_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        # Use Url codes as ids because ids are not unique otherwise
        ue_urls_codes = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        ue_urls_codes_list = sorted(list(set(ue_urls_codes.sum())))

        for ue_id in ue_urls_codes_list:
            yield scrapy.Request(BASE_URL.format(ue_id), self.parse_main, cb_kwargs={"ue_id": ue_id})

    @staticmethod
    def parse_main(response, ue_id):

        ue_name, main_info = response.xpath("//td[@bgcolor='#0088B0']/font/text()").getall()[:2]
        ue_name = ue_name.strip("\n\t")
        years = main_info.split(" | ")[-1]

        section_txt = "//b[contains(text(), '{}')]/following::td[1]//text()"
        teachers = response.xpath(section_txt.format("Enseignant")).getall()
        teachers = list(set([t for t in teachers if t != '/']))

        languages = response.xpath(section_txt.format("Langue")).get()
        languages = [LANGUAGES_DICT[lang] for lang in languages.split(" - ")] if languages else []

        # Content
        contents = []
        sections = ['Acquis', 'Dispositif']
        for section in sections:
            content = response.xpath(section_txt.format(section)).get()
            contents += [content] if content else [""]
        content = "\n".join(contents)
        content = "" if content == '\n' else content

        yield {
            'id': ue_id,
            'name': ue_name,
            'year': years,
            'teachers': teachers,
            'languages': languages,
            'url': response.url,
            'content': content
        }
