from pathlib import Path
from abc import ABC

import scrapy
import base64

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'http://www.galileonet.be/extranet/DescriptifsDeCours/getListeGestionUE?ec=4'

BASE_DATA = {
    "section": "",
    "option": "YWxs",
    "bloc": "YWxs",
    "annee": "",
}

YEARS = {
    '2020-2021': 'MTIw',
    '2021-2022': 'MTIx',
    '2022-2023': 'MTIy'
}

PROGRAMS_CODE = {
    "SC": "Spécialisation en santé communautaire",
    "BIRSG (N)": "Bachelier infirmier responsable en soins généraux"
}


class ISSIGProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Institut Supérieur de Soins Infirmiers Galilée (ISSIG)
    """

    name = 'issig-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}issig_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        BASE_DATA["annee"] = YEARS[f"{YEAR}-{YEAR+1}"]

        for program_id, program_name in PROGRAMS_CODE.items():
            BASE_DATA["section"] = str(base64.b64encode(program_id.encode("utf-8")), 'utf-8')
            yield scrapy.http.FormRequest(
                BASE_URL,
                callback=self.parse_main,
                formdata=BASE_DATA,
                cb_kwargs={'program_id': program_id, 'program_name': program_name}
            )

    @staticmethod
    def parse_main(response, program_id, program_name):

        row_txt = '//tr[@data-id]'
        ue_ids = response.xpath(f"{row_txt}/td[1]/text()").getall()
        ects = response.xpath(f"{row_txt}/td[5]/text()").getall()
        ects = [int(float(e)) for e in ects]

        cycle = 'bac' if 'Bachelier' in program_name else 'other'

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculties": ["Soins infirmiers"],
            "campuses": ["Bruxelles"],
            "url": response.url,
            "courses": ue_ids,
            "ects": ects
        }
