# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://fiches-ue.icampusferrer.eu/locked_list.php"

# TODO: check each year this list
SECTION_CAMPUS_PROGR = {
    "AA": ['Arts Appliqués', 'Site Palais du Midi',
           ["Arts du tissu", "Publicité", "Styliste et modéliste"]],
    "EcoB": ['Economique', 'Site Anneessens',
             ["Assurances", "Comptabilité", "Management de la logistique",
              "Sciences administratives et gestion publique"]],
    "EcoM": ['Economique', 'Site Anneessens',
             ["Expertise comptable et fiscale", "Gestion de l'entreprise",
              "Gestion publique", "Ingénieur commercial", "Master en sciences administratives",
              "Sciences commerciales"]],
    "ParaMed": ['Paramédical', 'Site Brugmann',
                ["Technologue de laboratoire m�dical", "Santé mentale et psychiatrie", "Sage-femme",
                 "Infirmier responsable de soins g�n�raux", "Soins infirmiers"]],
    "Peda": ['Pédagogique', 'Site Lemonnier',
             ["Certificat inter hautes écoles en didactique du néerlandais langue II et d'immersion",
              "Agrégation de l'enseignement secondaire supérieur",
              "Bachelier en enseignement section 1", "Bachelier en enseignement section 2",
              "Bachelier en enseignement section 3", "Normale Préscolaire", "Normale primaire",
              "Normale secondaire", "Préparation physique et entraînement"]],
    "Soc": ['Social', 'Site Anneessens', ["Gestion des ressources humaines"]],
    "Tech": ['Technique', 'Site Palais du Midi', ["Electronique",  "Techniques graphiques"]]
}


class HEFERRERProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Haute Ecole Francisco Ferrer
    """

    name = "he-ferrer-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}he-ferrer_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    @staticmethod
    def parse_main(response):

        ue_codes = [url.split("id=")[1].split("&")[0] for url in response.xpath("//tr//td[1]/a/@href").getall()]
        sub_programs = response.xpath("//tr//td[4]/text()").getall()
        df = pd.DataFrame({'ue': ue_codes, 'program': sub_programs})
        for section_code, (section, campus, main_programs) in SECTION_CAMPUS_PROGR.items():

            for i, main_program in enumerate(main_programs):

                associated_sub_programs = sorted(list(set(df[df["program"].str.contains(main_program)]["program"])))
                for j, sub_program in enumerate(associated_sub_programs):

                    cycle = 'bac'
                    if 'Certificat' in main_program:
                        cycle = 'certificate'
                    elif 'Agrégation' in main_program:
                        cycle = 'grad'
                    elif section_code == 'EcoM' and ('Master' in sub_program or not sub_program.endswith(" - ")):
                        cycle = 'master'

                    yield {
                        "id": f"{section_code}-{i}-{j}",
                        "name": sub_program.strip(" - "),
                        "cycle": cycle,
                        "faculties": [section],
                        "campuses": [campus],
                        "url": response.url,
                        "courses": df[df["program"] == sub_program]['ue'].to_list(),
                        "ects": []
                    }

