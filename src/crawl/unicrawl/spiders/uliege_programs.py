from abc import ABC

import scrapy

from config.utils import cleanup
from config.settings import YEAR

# TODO: maybe it's possible to check the year?
BASE_URL = "https://www.programmes.uliege.be/cocoon/recherche.html?source=formation"
PROGRAM_URL = "https://www.programmes.uliege.be{}"

FACULTY_DICT = {"archi": "Faculté d'Architecture",
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
    name = 'uliege-programs'
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/uliege_programs_{YEAR}.json',
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
            base_dict = {"id": program_id}
            yield scrapy.Request(url=PROGRAM_URL.format(link.replace('formations', 'programmes')),
                                 callback=self.parse_program,
                                 cb_kwargs={'base_dict': base_dict})

    @staticmethod
    def parse_program(response, base_dict):
        name = response.xpath("//h1/text()").get()
        cycle = response.xpath("//div[@class='u-courses-header__headline']/text()").get().split("/")[1][1:]
        campus = cleanup(response.xpath("//li[svg[@class='u-icon icon-icons-worldmap']]").get())

        # Faculty
        faculty_link = cleanup(response.xpath("//ul[@class='u-courses-sidebar__list--links']"
                                              "//li/a[@class='u-link' and "
                                              "contains(text(), 'La Faculté')]/@href").get())
        # Convert address to faculty
        faculty = FACULTY_DICT[[key for key in FACULTY_DICT.keys() if key in faculty_link][0]]

        courses = response.xpath("//th[@class='u-courses-cell--code']/a/text()").getall()
        ects = response.xpath("//td[@class='u-courses-cell--data--credits']/text()").getall()

        cur_dict = {"name": name,
                    "cycle": cycle,
                    "campus": campus,
                    "faculty": faculty,
                    "courses": courses,
                    "ects": ects}

        yield {**base_dict, **cur_dict}
