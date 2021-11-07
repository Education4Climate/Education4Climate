# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.heldb.be/ficheue/{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}heldb_programs_{YEAR}.json')

LANGUAGE_DICT = {
    "Français": "fr",
    "Anglais": "en",
    "Allemand": "de",
    "Néerlandais": "nl",
    "Espagnol": 'es',
    "Italien": 'it'
}


class HELDBCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Haute Ecole Lucia de Brouckère
    """

    name = "heldb-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}heldb_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        ue_urls_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["ue_urls_ids"]
        ue_urls_ids_list = sorted(list(set(ue_urls_ids.sum())))

        for ue_url_id in ue_urls_ids_list:
            yield scrapy.Request(BASE_URL.format(ue_url_id), self.parse_ue)

    @staticmethod
    def parse_ue(response):

        ue_name = response.xpath("//div[@name='titleue']//h1/text()").get()
        div_txt = "//div[contains(@class, 'container-fluid')]"
        ue_id = response.xpath(f"{div_txt}//span[contains(text(), 'Acronyme')]/following::span[1]/text()").get()

        lang = response.xpath(f"{div_txt}//span[contains(text(), \"Langue(s) d'enseignement\")]"
                              f"/following::span[1]/text()").get()
        languages = lang.strip(" \n").split(" ")
        languages = [LANGUAGE_DICT[l.strip("\n")] for l in languages if l != '']
        languages = ["fr"] if len(languages) == 0 else languages

        teachers = response.xpath(f"{div_txt}//strong[text()='Enseignant responsable : ']"
                                  f"/following::a[1]/text()").getall()
        sup_teachers = response.xpath(f"{div_txt}//strong[contains(text(), \"Autre(s) enseignant(s) de l'UE\")]"
                                      f"/following::a[1]/text()").getall()
        teachers += sup_teachers
        teachers = [t.lower().title() for t in teachers]

        year = cleanup(response.xpath(f"{div_txt}//div[@id='anac']//i").get()).split("Année académique ")[1]

        campus = cleanup(response.xpath(f"{div_txt}//p[span[contains(text(), \"Coordonnées du service\")]]").get())
        campus = 'Jodoigne' if 'Jodoigne' in campus else 'Anderlecht'

        def get_section_text(section_name):
            return cleanup(response.xpath(f"{div_txt}//div[p/span[contains(text(), '{section_name}')]]"
                                          f"/following::div[1]").get()).replace("\n             ", ' ')
        content = get_section_text('Descriptif')
        goal = get_section_text('Contribution')

        yield {
            "id": ue_id,
            "name": ue_name,
            "year": year,
            "languages": languages,
            "teachers": teachers,
            "url": response.url,
            "campuses": [campus],
            "content": content,
            "goal": goal,
            "activity": '',
            "other": ''
        }
