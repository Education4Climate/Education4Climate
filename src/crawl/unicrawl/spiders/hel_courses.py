# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = f"http://p4580.phpnet.org/{YEAR}-{YEAR+1}/XtractUE/DetailsUE/" + "{}.html"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}hel_programs_{YEAR}.json')

LANGUAGE_DICT = {"Français": "fr",
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


class HELCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for Haute Ecole de la Ville de Liège
    """

    name = "hel-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}hel_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        ue_urls_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["ue_urls_ids"]
        ue_urls_ids_list = sorted(list(set(ue_urls_ids.sum())))

        for ue_url_id in ue_urls_ids_list:
            yield scrapy.Request(BASE_URL.format(ue_url_id), self.parse_ue)

    @staticmethod
    def parse_ue(response):

        ue_id = response.xpath("//td[@class='important_ue'and @colspan=2]/text()").get().strip(": ")
        ue_name = response.xpath("//td[@class='important_ue'and @colspan=4]/text()").get().split(": ")[1]

        info_par = response.xpath("//tr[@class='entete']//p").get()
        year = info_par.split("Année académique</b> : ")[1].split('<br>')[0]
        ects = int(info_par.split("Nombre de crédits</b> : ")[1].split('<br>')[0])
        campus = info_par.split("Implantation(s)</b> : ")[1].split('<br>')[0].strip(" ")

        teachers = cleanup(response.xpath("//table[@class='table_aa_profs_heures']/tbody/tr/td[2]").getall())
        teachers = [t.strip(",").replace(" ", " ").strip(" ") for t in teachers]

        languages = response.xpath("//b[contains(text(), 'Langue')]/following::text()[1]").getall()
        languages = [LANGUAGE_DICT[l.strip(" ")] for l in languages]

        contents = [cleanup(response.xpath("//div[@id='liste_capacites_retenues']").get()),
                    cleanup(response.xpath("//div[@class='module_aa']").get())]
        content = "\n".join(contents)
        content = "" if content == "\n" else content

        yield {
            "id": ue_id,
            "name": ue_name,
            "year": year,
            "languages": languages,
            "teachers": teachers,
            "ects": ects,
            "campus": campus,
            "url": response.url,
            "content": content
        }


