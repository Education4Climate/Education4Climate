from pathlib import Path
from abc import ABC

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'https://www.einet.be/ects/affichelisteects_public.php'

BASE_DATA = {
    "anneeacaderef": f"{YEAR}_{YEAR+1}",
    "choixsection": "",
    "choixannee": "",
    "coderetour": "listepublic",
    "codemarcourtx": "19",
}

PROGRAMS_CODE = {
    "ECSEDI": "Bachelier Assitant de Direction",
    "ISALT": "Bachelier en Management du Tourisme et Loisirs"
}


class ECSEDIISALTProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for ECSEDI-ISALT Bruxelles
    """

    name = 'ecsedi-isalt-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ecsedi-isalt_programs_{YEAR}_pre.json').as_uri()
    }

    def start_requests(self):

        for program_id, program_name in PROGRAMS_CODE.items():
            BASE_DATA["choixsection"] = program_id
            print(BASE_DATA)
            for i in range(1, 4):
                BASE_DATA["choixannee"] = str(i)
                yield scrapy.http.FormRequest(
                    BASE_URL,
                    callback=self.parse_main,
                    formdata=BASE_DATA,
                    cb_kwargs={'program_id': program_id, 'program_name': program_name}
                )

    @staticmethod
    def parse_main(response, program_id, program_name):

        row_txt = "//tr[@bgcolor='#ffffff']"
        ue_links = response.xpath(f"{row_txt}/td[4]/a/@onclick").getall()
        ue_ids = [ue_link.split("code=")[1].split("&")[0] for ue_link in ue_links]
        ects = response.xpath(f"{row_txt}/td[6]/font/text()").getall()
        ects = [int(e) for e in ects]

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": 'bac',
            "faculties": ["Département Economique"],
            "campuses": ["Bruxelles"],
            "url": response.url,
            "courses": ue_ids,
            "ects": ects
        }



