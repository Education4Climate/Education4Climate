from pathlib import Path

import scrapy
from abc import ABC

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'http://extranet.ihecs.be/?ects=go&act=showlist'

BASE_DATA = {
    "anneeaca": f"{YEAR}_{YEAR+1}",
    "anneeacaderef": "",
    "choixsection": "",
    "choixannee": "",
}

PROGRAMS_CODE = {"BCA": "Bachelier en Communication Appliquée",
                 "PI": "Master en presse et information",
                 "RP": "Master en relations publiques",
                 "PUB": "Master en Publicité",
                 "ASCEP": "Master en animation socio-culturelle et Education permanente",
                 "EAM": "Master en education aux médias",
                 "ME": "Master en Management d'événements"}


class IHECSProgramSpider(scrapy.Spider, ABC):
    name = 'ihecs-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ihecs_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        for progam_id, program_name in PROGRAMS_CODE.items():
            BASE_DATA["choixsection"] = progam_id
            yield scrapy.http.FormRequest(
                BASE_URL,
                callback=self.parse_main,
                formdata=BASE_DATA,
                cb_kwargs={'program_id': progam_id, 'program_name': program_name}
            )

    def parse_main(self, response, program_id, program_name):

        # ues = response.xpath("//tr[@bgcolor='#e5f2f7']/td[1]/font/text()").getall()
        ects = response.xpath("//tr[@bgcolor='#e5f2f7']/td[4]/font/text()").getall()
        ects = [int(e) for e in ects]
        # Use Url codes as ids because ids are not unique otherwise
        ues_urls = response.xpath("//tr[@bgcolor='#e5f2f7']/td[5]/font/a/@href").getall()
        ues_urls_codes = [link.split("codeue=")[1].split("&")[0] for link in ues_urls]

        cycle = 'bac' if 'Bachelier' in program_name else 'master'

        yield {
            "id": program_id,
            "name": program_name,
            "cycle": cycle,
            "faculty": "Journalism & Communication",
            "campus": "Bruxelles",
            "courses": ues_urls_codes,
            "ects": ects
        }



