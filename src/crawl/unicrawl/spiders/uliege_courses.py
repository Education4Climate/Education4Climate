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

        course_name = cleanup(response.css("h1::text").get())
        year_and_id = cleanup(
            response.xpath("//div[@class='u-courses-header__headline']/text()")
            .get()).strip(" ").split("/")
        course_id = year_and_id[1].strip(" ")
        years = year_and_id[0]

        # Get teachers name (not an easy task because not a constant syntax)
        teachers_para = response.xpath("//section[h3[contains(text(),'Enseignant')"
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
        teachers = [t for t in teachers if "N..." not in t]
        teachers = [t.replace(' ', ' ') for t in teachers]
        teachers = [t.replace('  ', ' ') for t in teachers]
        # Put surname first
        teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]
        teachers = list(set(teachers))

        # Language
        languages = cleanup(response.xpath(".//section[h3[contains(text(), "
                                           "\"Langue(s) de l'unité d'enseignement\")]]/p").getall())
        languages = [LANGUAGE_DICT[lang] for lang in languages]

        # Course description
        def get_sections_text(sections_names):
            texts = [cleanup(response.xpath(f".//section[h3[contains(text(), \"{section}\")]]").get())
                     .replace(f"{section}", "").strip("\n")
                     for section in sections_names]
            return "\n".join(texts).strip("\n ")
        content = get_sections_text(["Contenus de l'unité d'enseignement"])
        goal = get_sections_text(["Acquis d'apprentissage (objectifs d'apprentissage) de l'unité d'enseignement"])
        activity = get_sections_text(["Activités d'apprentissage prévues et méthodes d'enseignement"])

        yield {
            'id': course_id,
            'name': course_name,
            'year': years,
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            'content': content,
            'goal': goal,
            'activity': activity,
            'other': ''
        }
