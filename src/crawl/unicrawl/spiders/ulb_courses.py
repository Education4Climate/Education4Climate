import json
import urllib.parse
from abc import ABC
from pathlib import Path

import scrapy

from config.settings import YEAR

PATH_COURS_URL = urllib.parse.quote(
    '/ws/ksup/course-programmes?anac={}&mnemonic={}&lang=fr',
    safe='{}'
)

COURS_URL = f'https://www.ulb.be/api/formation?path={PATH_COURS_URL}'

PROG_DATA_PATH = Path(f'../../data/crawling-output/ulb_programs_{YEAR}.json')


class ULBSpider(scrapy.Spider, ABC):
    name = 'ulb-courses'
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/ulb_courses_{YEAR}.json',
    }

    def start_requests(self):

        progs = json.loads(PROG_DATA_PATH.read_text('utf-8'))

        list_cours = []
        for prog in progs:
            list_cours += prog['courses']

        for cours in sorted(set(list_cours)):
            base_dict = {
                'url': f'https://www.ulb.be/fr/programme/{cours.lower()}',
                'anacs': f'{YEAR}-{int(YEAR) + 1}',
                'shortname': cours
            }

            yield scrapy.Request(
                url=COURS_URL.format(YEAR, cours),
                callback=self.parse_cours,
                cb_kwargs={'base_dict': base_dict}
            )

    @staticmethod
    def parse_cours(response, base_dict):

        json_obj = json.loads(json.loads(response.text)['json'])

        # TODO : Finir le scraper lorsque le site remarchera

        cur_dict = {
            "teachers": None,
            "credits": None,
            "language": None,
            "content": None,
            "goal": None,
            "prerquisite": None,
            "method": None,
            "other": None,
            "evaluation": None,
            "name": None,
            "class": None
        }

        yield {**base_dict, **cur_dict}

# cur_dict = {
#     "url": "https://www.ulb.be/fr/programme/2019-tran-b100",
#     "anacs": "2020-2021",
#     "teachers": [
#         "\nSylvain DELCOMMINETTE (Coordonnateur)", "Didier DEBAISE",
#         "Odile GILON", "Arnaud PELLETIER", "Luc Libert"
#     ],
#     "credits": "5",
#     "language": "fran\u00e7ais",
#     "content": "Philosophie ancienne, philosophie m\u00e9di\u00e9vale, philosophie "
#                "moderne et philosophie contemporaine.",
#     "goal": "Philosophie ancienne, philosophie m\u00e9di\u00e9vale, "
#             "philosophie moderne et philosophie contemporaine.",
#     "prerquisite": "Philosophie ancienne, philosophie m\u00e9di\u00e9vale, "
#                    "philosophie moderne et philosophie contemporaine.",
#     "method": "Philosophie ancienne, philosophie m\u00e9di\u00e9vale, "
#               "philosophie moderne et philosophie contemporaine.",
#     "other": "Philosophie ancienne, philosophie m\u00e9di\u00e9vale, "
#              "philosophie moderne et philosophie contemporaine.",
#     "evaluation": "Philosophie ancienne, philosophie m\u00e9di\u00e9vale, "
#                   "philosophie moderne et philosophie contemporaine.",
#     "shortname": "TRAN-B100",
#     "name": "Histoire de la philosophie",
#     "class": "Histoire de la philosophie"
# }
