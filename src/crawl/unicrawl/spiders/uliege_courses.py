from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.programmes.uliege.be/cocoon/cours/{}.html"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}uliege_programs_{YEAR}.json')
LANGUAGE_DICT = {"Langue française": 'fr',
                 "Langue anglaise": 'en',
                 "Langue allemande": 'de',
                 "Langue néerlandaise": 'nl',
                 "Langue italienne": "it",
                 "Langue espagnole": "es"}


class ULiegeCourseSpider(scrapy.Spider, ABC):
    name = "uliege-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}uliege_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URL.format(course_id, YEAR), self.parse_main)

    @staticmethod
    def parse_main(response):

        class_name = cleanup(response.css("h1::text").get())
        year_and_short_name = cleanup(
            response.xpath("//div[@class='u-courses-header__headline']/text()")
            .get()).strip(" ").split("/")
        short_name = year_and_short_name[1].strip(" ")
        years = year_and_short_name[0]

        # Get teachers name (not an easy task because not a constant syntax)
        teachers_para = response.xpath(".//section[h3[contains(text(),'Enseignant')"
                                       " or contains(text(),'Suppléant')"
                                       " or contains(text(),'Coordinateur')]]/p")
        # Check first if there are links (to teachers page)
        teachers_links = teachers_para.xpath(".//a").getall()
        if len(teachers_links) == 0:
            teachers = cleanup(teachers_para.get()).split(", ")
        else:
            teachers = cleanup(teachers_links)
        teachers = [] if teachers == [""] else teachers
        # Replace strange characters
        teachers = [t for t in teachers if "N..." in t]
        teachers = [t.replace(' ', ' ') for t in teachers]
        teachers = [t.replace('  ', ' ') for t in teachers]
        # Put surname first
        teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]
        teachers = list(set(teachers))

        # Language
        languages = cleanup(response.xpath(".//section[h3[contains(text(), "
                                           "\"Langue(s) de l'unité d'enseignement\")]]/p").getall())
        languages = [LANGUAGE_DICT[lang] for lang in languages]

        # Content of the class
        sections = ["Contenus de l'unité d'enseignement",
                    "Acquis d'apprentissage (objectifs d'apprentissage) de l'unité d'enseignement",
                    "Activités d'apprentissage prévues et méthodes d'enseignement"]
        contents = []
        for section in sections:
            content = cleanup(response.xpath(f".//section[h3[contains(text(), \"{section}\")]]").get())
            content = content.replace(f"{section}", "").strip("\n")
            contents += [content]
        content = "\n".join(contents)
        content = "" if content == "\n\n" else content

        data = {
            'id': short_name,
            'name': class_name,
            'year': years,
            'teachers': teachers,
            'languages': languages,
            'url': response.url,
            'content': content,
        }

        yield data
