# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = "https://www.einet.be/ficheueprintable.php?code={}" + \
           f"&anneeaca={YEAR}_{YEAR+1}&codemarcourt=19"
ECTS_URL = "https://www.einet.be/ficheectsprintable.php?code={}" + \
           f"&anneeaca={YEAR}_{YEAR+1}&codemarcourt=19"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}ecsedi-isalt_programs_{YEAR}.json')

LANGUAGES_DICT = {
    "français": "fr",
    "Français": "fr",
    "Langue française": "fr",
    "Anglais": "en",
    "Allemand": "de",
    "Néerlandais": "nl",
    "Italien": "it",
    "chinois": 'cn',
    "Chinois": 'cn',
    "espagnol": 'es',
    "Espagnol": 'es'
}


class ECSEDIISALTCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for ECSEDI-ISALT Bruxelles
    """

    name = "ecsedi-isalt-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ecsedi-isalt_courses_{YEAR}_pre.json').as_uri()
    }

    def start_requests(self):

        # Use Url codes as ids because ids are not unique otherwise
        ue_codes = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        ue_codes_list = sorted(list(set(ue_codes.sum())))

        for ue_id in ue_codes_list:
            yield scrapy.Request(BASE_URL.format(ue_id), self.parse_main, cb_kwargs={"ue_id": ue_id})

    def parse_main(self, response, ue_id):

        ue_name = response.xpath("//h55/text()").get()
        years = response.xpath("//h5/b[contains(text(), 'Unité')]/text()").get().split(" ")[0]

        # Not consistent enough
        teachers = []

        languages = response.xpath("//i[contains(text(), 'Langue')]"
                                   "/following::font[1]/text()").get()
        languages = [LANGUAGES_DICT[l] for l in languages.split(" - ") if l in LANGUAGES_DICT]
        languages = ["fr"] if len(languages) == 0 else languages

        base_dict = {
            'id': ue_id,
            'name': ue_name,
            'year': years,
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            'content': '',
            'goal': '',
            'activity': '',
            'other': ''
        }

        # Content
        activities_urls = response.xpath("//i[contains(text(), 'Activités')]/following::font[1]//a//@onclick").getall()
        if len(activities_urls) != 0:
            activities_ids = [link.split("code=")[1].split("&")[0] for link in activities_urls]
            for activity_id in activities_ids:
                print(response.url, activity_id)
                yield scrapy.Request(ECTS_URL.format(activity_id), self.parse_content,
                                     cb_kwargs={"base_dict": base_dict})

        else:
            base_dict['content'] = cleanup(response.xpath("//i[contains(text(), 'Contenu')]/following::font[1]").get())
            base_dict['goal'] = cleanup(response.xpath("//i[contains(text(), 'Acquis')]/following::font[1]").get())
            yield base_dict

    @staticmethod
    def parse_content(response, base_dict):
        base_dict['content'] = cleanup(response.xpath("//i[contains(text(), 'Contenu')]/following::font[1]").get())
        base_dict['goal'] = cleanup(response.xpath("//i[contains(text(), 'Acquis')]/following::font[1]").get())
        yield base_dict
