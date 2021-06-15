from pathlib import Path
from abc import ABC

import scrapy
import base64

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'http://www.galileonet.be/extranet/DescriptifsDeCours/getListeGestionUE'

BASE_DATA = {
    "section": "",
    "option": "YWxs",
    "bloc": "YWxs",
    "annee": "",
}

YEARS = {'2020-2021': 'MTIw',
         '2021-2022': 'MTIx'}

PROGRAMS_CODE = {"PRIMA": "Instituteur primaire",
                 "PRESC": "Instituteur préscolaire",
                 "AESI": "Enseignant en "}


OPTIONS = {"PA": "Arts plastiques",
           "FF": "Français et français langue étrangère",
           "FR": "Français et religion",
           "LG": "Langue germaniques",
           "MA": "Mathématiques",
           "SE": "Sciences économiques",
           "SH": "Sciences humaines",
           "SN": "Sciences naturelles"}


class ISPGProgramSpider(scrapy.Spider, ABC):
    name = 'ispg-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ispg_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        BASE_DATA["annee"] = YEARS[f"{YEAR}-{YEAR+1}"]

        for program_id, program_name in PROGRAMS_CODE.items():
            BASE_DATA["section"] = str(base64.b64encode(program_id.encode("utf-8")), 'utf-8')
            if program_id == 'AESI':
                for option_id, option_name in OPTIONS.items():
                    BASE_DATA['option'] = str(base64.b64encode(option_id.encode("utf-8")), 'utf-8')
                    # call()
                    yield scrapy.http.FormRequest(
                        BASE_URL,
                        callback=self.parse_main,
                        formdata=BASE_DATA,
                        cb_kwargs={'program_id': program_id + '-' + option_id,
                                   'program_name': program_name + option_name}
                    )
            else:
                yield scrapy.http.FormRequest(
                    BASE_URL,
                    callback=self.parse_main,
                    formdata=BASE_DATA,
                    cb_kwargs={'program_id': program_id, 'program_name': program_name}
                )

    def parse_main(self, response, program_id, program_name):

        row_txt = '//tr[@data-id]'
        ue_ids = response.xpath(f"{row_txt}/td[1]/text()").getall()
        ects = response.xpath(f"{row_txt}/td[5]/text()").getall()
        ects = [int(e) for e in ects]

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": 'bac',
            "faculty": "Pédagogie",
            "campus": "Bruxelles",
            "courses": ue_ids,
            "ects": ects,
        }



