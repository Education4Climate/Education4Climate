from abc import ABC
from pathlib import Path

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.programmes.uliege.be/cocoon/recherche.html?source=formation"
PROGRAM_URL = "https://www.programmes.uliege.be{}"

FACULTY_DICT = {
    "archi": "Faculté d'Architecture",
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


class ULiegeSpider(scrapy.Spider, ABC):
    """
    Programs crawler for ULiège
    """

    name = 'uliege-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}uliege_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(
            url=BASE_URL,
            callback=self.parse_main
        )

    def parse_main(self, response):

        links = response.xpath("//td[@class='u-courses-results__row__cell--link']/a/@href").getall()
        program_ids = [link.split("/")[-1].split(".")[0] for link in links]

        for program_id, link in zip(program_ids, links):
            yield scrapy.Request(url=PROGRAM_URL.format(link.replace('formations', 'programmes')),
                                 callback=self.parse_program,
                                 cb_kwargs={'program_id': program_id})

    @staticmethod
    def parse_program(response, program_id):

        program_name = response.xpath("//h1/text()").get()
        if program_name is None:
            return

        cycle = response.xpath("//div[@class='u-courses-header__headline']/text()").get().split("/")[1][1:]
        if cycle == 'Bachelier':
            cycle = 'bac'
        elif 'Master' in cycle:
            cycle = 'master'
        elif 'Certificat' in cycle:
            cycle = 'certificate'
        elif cycle == 'Formation doctorale':
            cycle = 'doctor'
        else:
            cycle = 'other'

        campus = cleanup(response.xpath("//li[svg[@class='u-icon icon-icons-worldmap']]").get())
        campuses = [campus] if campus != "" else  []

        # Faculty
        faculty_link = cleanup(response.xpath("//ul[@class='u-courses-sidebar__list--links']"
                                              "//li/a[@class='u-link' and "
                                              "contains(text(), 'La Faculté')]/@href").get())
        # Convert address to faculty
        faculty = FACULTY_DICT[[key for key in FACULTY_DICT.keys() if key in faculty_link][0]]

        courses = response.xpath("//th[@class='u-courses-cell--code']/a/text()").getall()
        ects = response.xpath("//th[@class='u-courses-cell--code']"
                              "/following::td[@class='u-courses-cell--data--credits'][1]/text()").getall()
        ects = [int(e) for e in ects]

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculties": [faculty],
            "campuses": campuses,
            "url": response.url,
            "courses": courses,
            "ects": ects
        }
