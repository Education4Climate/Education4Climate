from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from config.utils import cleanup
from config.settings import YEAR

BASE_URL = "https://www.programmes.uliege.be/cocoon/cours/{}.html"
PROG_DATA_PATH = Path(f'../../data/crawling-output/uliege_programs_{YEAR}.json')
LANGUAGE_DICT = {"Langue française": 'fr',
                 "Langue anglaise": 'en',
                 "Langue allemande": 'de',
                 "Langue néerlandaise": 'nl',
                 "Langue italienne": "it",
                 "Langue espagnole": "es"}


class ULiegeCourseSpider(scrapy.Spider, ABC):
    name = "uliege-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/uliege_courses_{YEAR}.json',
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
        teachers_para = response.xpath(".//section[h3[contains(text(),'Enseignant')]]/p")
        # Check first if there are links (to teachers page)
        teachers_links = teachers_para.xpath(".//a").getall()
        if len(teachers_links) == 0:
            teachers = cleanup(teachers_para.getall())
        else:
            teachers = cleanup(teachers_links)

        # Language
        languages = cleanup(response.xpath(".//section[h3[contains(text(), "
                                           "\"Langue(s) de l'unité d'enseignement\")]]/p").getall())
        languages = [LANGUAGE_DICT[lang] for lang in languages]

        # Content of the class
        content = cleanup(response.xpath(".//section[h3[contains(text(), "
                                         "\"Contenus de l'unité d'enseignement\")]]").get()) + " "
        content += cleanup(response.xpath(".//section[h3[contains(text(), \"Acquis d'apprentissage\")]]").get()) + " "
        content += cleanup(response.xpath(".//section[h3[contains(text(), \"Activités d'apprentissage\")]]").get())

        # TODO: add back if data for program not manageable
        """
        # Cycle and credits
        credit_lines = cleanup(
            response.xpath(".//section[h3[contains(text(), 'Nombre de crédits')]]"
                           "//tr/td[@class='u-courses-results__row__cell--list']").getall())
        cycles = []
        ects = []
        programs = []
        for i, el in enumerate(credit_lines):
            # Program name
            if i % 2 == 0:
                programs += [el]
                if 'Master' in el:
                    cycles += ["master"]
                elif 'Bachelier' in el:
                    cycles += ["bachelier"]
                elif 'Erasmus' in el:
                    cycles += ["erasmus"]
                else:
                    cycles += [el]
            # Credit number
            else:
                ects += [int(el.split(" ")[0])]
        """

        data = {
            'name': class_name,
            'id': short_name,
            'year': years,
            'teacher': teachers,
            'language': languages,
            # 'cycle': cycles,
            # 'ects': ects,
            'url': response.url,
            'content': content,
            # 'faculty': '',
            # 'campus': '',
            # 'program': programs
        }

        yield data

        # TODO: add back if data for program not manageable
        """
        # The links to the programs are written in a relative manner
        program_links = response.xpath(".//section[h3[contains(text(), 'Nombre de crédits')]]"
                                       "//tr/td[@class='u-courses-results__row__cell--link']/a/@href").getall()
        data['programlinks'] = program_links
        if len(program_links) != 0:

            for link in program_links:
                yield response.follow(link, callback=self.parse_faculty_and_campus, meta=data,
                                      dont_filter=True)
        else:
            yield data
        """

    """
    @staticmethod
    def parse_faculty_and_campus(response):
        data = response.meta
        # Campus
        data['campus'] = cleanup(
            response.xpath("//li[svg[@class='u-icon icon-icons-worldmap']]").get())

        # Faculty
        faculty_link = cleanup(response.xpath("//ul[@class='u-courses-sidebar__list--links']"
                                                "//li/a[@class='u-link' and "
                                                "contains(text(), 'La Faculté')]/@href").get())
        # Convert address to faculty
        faculty_dict = {"archi": "Faculté d'Architecture",
                        "droit": "Faculté de Droit, Science politique et Criminologie",
                        "gembloux": "Gembloux Agro-Bio Tech",
                        "hec": "HEC Liège - Ecole de Gestion",
                        "facmed": "Faculté de Médecine",
                        "fmv": "Faculté de Médecine Vétérinaire",
                        "facphl": "Faculté de Philosophie et Lettres",
                        "fapse": "Faculté de Psychologie, Logopédie et Sciences de l'Education",
                        "facsc": "Faculté des Sciences",
                        "facsa": "Faculté des Sciences Appliquées",
                        "ishs": "Faculté des Sciences Sociales"
                        }
        data["faculty"] = faculty_dict[
            [key for key in faculty_dict.keys() if key in faculty_link][0]]

        keys = ['name', 'id', 'year', 'teacher', 'language', 'cycle',
                'ects', 'content', 'url', 'faculty', 'campus', 'program']
        data = {key: data[key] for key in keys}
        yield data
    """
