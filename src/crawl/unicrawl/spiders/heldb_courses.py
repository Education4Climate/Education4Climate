# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = f"https://www.heldb.be/ficheue-{YEAR-2000}/" + "{}"
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

        div_txt = "//div[contains(@class, 'container-fluid')]"

        ue_name = response.xpath(f"{div_txt}//div[contains(@class, 'col-9')]/h1/strong/text()").get()
        ue_id = response.xpath(f"{div_txt}//p[strong[contains(text(), 'Acronyme')]]/text()[3]").get().strip("\n ")

        languages = response.xpath(f"{div_txt}//span[@class='badge bg-info']/text()").getall()
        languages = [LANGUAGE_DICT[l.strip("\n")] for l in languages if l != '']
        languages = list(set(languages))
        languages = ["fr"] if len(languages) == 0 else languages

        teachers = response.xpath(f"{div_txt}//strong[contains(text(), 'Enseignant(s) responsable')]"
                                  f"/following::a[1]/text()").getall()
        teachers += response.xpath(f"{div_txt}//strong[contains(text(), 'Autre(s) enseignant')]"
                                   f"/following::a[1]/text()").getall()
        teachers = [t.title() for t in teachers]
        # remove Monsieur Madame
        teachers = [" ".join(t.split(" ")[1:]) if "Monsieur" in t or "Madame" in t else t for t in teachers]
        # invert first name and family name
        teachers = [(" ".join(teacher.split(" ")[1:]) + " " + teacher.split(" ")[0]).strip(" ") for teacher in teachers]

        year = response.xpath(f"{div_txt}//i[contains(text(), 'Année académique')]/text()").get()
        year = year.split("Année académique ")[1]

        campus = cleanup(response.xpath(f"{div_txt}//p[strong[contains(text(), \"Coordonnées du service\")]]").get())
        campus = 'Jodoigne' if 'Jodoigne' in campus else 'Anderlecht'

        contents = cleanup(response.xpath(f"{div_txt}//h5[contains(text(), 'Contenu')]//following::ul[1]").getall())
        content = "\n".join(contents).strip("\n")

        goals = cleanup(response.xpath(f"{div_txt}//h5[contains(text(), 'Objectifs')]//following::ul[1]").getall())
        goals += cleanup(response.xpath(f"{div_txt}//div[h3[contains(text(), 'Acquis')]]//ul").getall())
        goal = "\n".join(goals).strip("\n")

        activities = cleanup(response.xpath(f"{div_txt}//div[h3[contains(text(), 'Activité')]]//ul").getall())
        activity = "\n".join(activities).strip("\n")

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
            "activity": activity,
            "other": ''
        }
