# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy
import base64
import itertools

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = "http://www.galileonet.be/extranet/DescriptifsDeCours/getViewGestionUE?cue={}&ec=4"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}issig_programs_{YEAR}.json')

LANGUAGES_DICT = {
    "Français": ["fr"],
    "Anglais": ["en"],
    "Allemand": ["de"],
    "Néerlandais": ["nl"],
    "AnglaisNéerlandais": ["en", "nl"],
    "FrançaisAnglais": ["fr", "en"],
    "FrançaisNéerlandaisAnglais": ["fr", "nl", "en"]
}


class ISSIGCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Institut Supérieur de Soins Infirmiers Galilée (ISSIG)
    """

    name = "issig-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}issig_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        # Use Url codes as ids because ids are not unique otherwise
        ue_codes = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        ue_codes_list = sorted(list(set(ue_codes.sum())))

        for ue_id in ue_codes_list:
            converted_ue_id = str(base64.b64encode(ue_id.encode("utf-8")), 'utf-8')
            yield scrapy.Request(BASE_URL.format(converted_ue_id), self.parse_main, cb_kwargs={"ue_id": ue_id})

    @staticmethod
    def parse_main(response, ue_id):

        ue_name = response.xpath("//h5[2]/strong/text()").get().strip(" ")
        years = response.xpath("//h5[3]/text()").get().strip(" ").split(" ")[-1]

        teachers = response.xpath("//div[@class='col-md-9']/text()").getall()
        teachers = [t.strip(" \n\t/") for t in teachers]
        teachers = [t for t in teachers if t != '']
        teachers = [t.split(", ") for t in teachers]
        teachers = list(set(itertools.chain.from_iterable(teachers)))
        teachers = [t.title() for t in teachers]

        languages = response.xpath("//div[label[@for='langueenseignement']]/text()[2]").get().strip(" \n")
        languages = LANGUAGES_DICT[languages] if len(languages) != 0 else ['fr']

        # Course description
        content = cleanup(response.xpath("//div[label[@for='descsynthUE']]/div").get())
        goal = cleanup(response.xpath("//div[label[@for='aas']]/div").get())

        yield {
            'id': ue_id,
            'name': ue_name,
            'year': years,
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            'content': content,
            'goal': goal,
            'activity': '',
            'other': ''
        }
