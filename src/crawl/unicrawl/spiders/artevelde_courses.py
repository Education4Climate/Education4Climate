# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = "https://bamaflexweb.arteveldehs.be/BMFUIDetailxOLOD.aspx?a={}&b=1&c=1"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}artevelde_programs_{YEAR}.json')

LANGUAGES_DICT = {"Nederlands": "nl",
                  "Engels": "en",
                  "Frans": "fr",
                  "Duits": "de",
                  "Spaans": "es",
                  "Latijn": "la",
                  "Chinees": "cn"}


class ArteveldeCourseSpider(scrapy.Spider, ABC):
    name = "artevelde-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}artevelde_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        ue_codes = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        ue_codes_list = sorted(list(set(ue_codes.sum())))

        print(len(ue_codes_list))
        for ue_id in ue_codes_list:
            yield scrapy.Request(BASE_URL.format(ue_id), self.parse_main, cb_kwargs={"ue_id": ue_id})

    @staticmethod
    def parse_main(response, ue_id):

        ue_name = response.xpath("//h2[contains(@id, 'ctl00')]/text()").get()

        years = response.xpath("//span[contains(@id, 'AcademiejaarOms')]/text()").get()
        years = years.split("-")[0] + "-20" + years.split("-")[1]

        ects = int(response.xpath("//span[contains(@id, 'Inhoud')]/text()").get().split("\xa0")[0])

        teacher_text = response.xpath("//span[contains(text(), 'Coördinator')]/following::span[1]/text()").get()
        teachers = [teacher_text] if teacher_text else []
        teacher_text = response.xpath("//span[contains(text(), 'ocenten')]/following::span[1]/text()").get()
        teachers += teacher_text.split(", ") if teacher_text else []

        language_text = response.xpath("//span[contains(text(), 'Onderwijstalen')]/following::span[1]/text()").get()
        languages = language_text.split(", ") if language_text else []
        languages = [LANGUAGES_DICT[l] for l in languages if l in LANGUAGES_DICT]

        # Content
        content = cleanup(response.xpath("//h4[contains(text(), 'Omschrijving Inhoud')]"
                                         "//following::div[1]").get())

        yield {
            'id': ue_id,
            'name': ue_name,
            'year': years,
            'teachers': teachers,
            'languages': languages,
            'ects': ects,
            'url': response.url,
            'content': content
        }
