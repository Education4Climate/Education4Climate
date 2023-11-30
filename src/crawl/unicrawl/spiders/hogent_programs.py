# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path
import json

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = f"https://studiefiches.hogent.be/index.cfm/fetch-study-programs?" \
           f"format=json&acadyear={YEAR}-{YEAR-2000+1}&lang=1"

PROGRAM_URL = f"https://studiefiches.hogent.be/index.cfm/modeltrajecten?" \
              f"acadyear={YEAR}-{YEAR-2000+1}" + "&opl={}&dep={}&lang=1"

MODEL_TRAJECT_URL = f"https://studiefiches.hogent.be/index.cfm/fetch-model-trajects?" \
                    f"format=json&acadyear={YEAR}-{YEAR-2000+1}" + "&opl={}&dep={}&lang=1"

COURSES_LIST_URL = "https://studiefiches.hogent.be/index.cfm/fetch-opleidingsonderdelen?format=json&mid={}" \
                   "&opl={}&dep={}" + f"&acadyear={YEAR}-{YEAR-2000+1}&lang=1"

# TODO: need to check this is the full list
FACULTIES_DICT = {
    'DBO': 'Departement Bedrijf en Organisatie',
    'DBT': 'Departement Biowetenschappen en Industriële Technologie',
    'DGZ': 'Departement Gezondheidszorg',
    'DIT': 'Departement IT en Digitale Innovatie',
    'DLO': 'Departement Lerarenopleiding',
    'DOG': 'Departement Omgeving',
    'DSA': 'Departement Sociaal-Agogisch Werk',
    'GO5': 'GO5 by HOGENT',
    'SCH': 'School of Arts KASK-Koninklijk Conservatorium'
}

CYCLES_DICT = {
    'ABA': 'bac',  # Academisch gerichte bacheloropleiding
    'BNB': 'bac',  # Bacheloropleiding die volgt op een bacheloropleiding
    'GRAD': 'grad',  # Graduaatsopleiding
    'INT': 'other',  # Programma voor inkomende uitwisselingsstudenten
    'MA': 'master',  # Masteropleiding
    'MNM': 'master',  # Masteropleiding die volgt op een masteropleiding
    'PBA': 'bac',  # Professioneel gerichte bacheloropleiding
    'PGR': 'postgrad',  # Postgraduaatopleiding
    'SCH': 'other',  # Schakelprogramma
    'VBP': 'other',  # Voorbereidingsprogramma
    'BIJNA': 'other'  # Bij-of nascholingsprogramma's
}


class HOGENTProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for HOGENT
    """

    name = "hogent-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}hogent_programs_{YEAR}_pre.json')
    }

    def start_requests(self):

        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):

        programs_list = response.json()
        for program_dict in programs_list:
            main_program_name = program_dict["OPLEIDING"]
            main_program_id = program_dict["OPLEIDINGCODE"]
            fac_code = program_dict["DEPARTEMENTCODE"]  # = FACULTEITCODE
            cycle = CYCLES_DICT[program_dict["BAMATYPEKORT"]]
            yield response.follow(MODEL_TRAJECT_URL.format(main_program_id, fac_code), self.parse_program,
                                  cb_kwargs={'main_program_name': main_program_name,
                                             'main_program_id': main_program_id,
                                             'fac_code': fac_code,
                                             'cycle': cycle})

    def parse_program(self, response, main_program_name, main_program_id, fac_code, cycle):

        # Convert faculty code to name
        faculties = [FACULTIES_DICT[fac_code]]

        trajects = response.json()

        for traject_id, traject in enumerate(trajects):
            traject_name = traject['DEELTRAJECT']

            program_id = f"{main_program_id}-{traject_id}"
            program_name = main_program_name + ' - ' + traject_name.title()
            for sub_traject in traject['ARRDEELTRAJECTEN']:
                sub_traject_id = sub_traject['modeltrajectid']

                base_dict = {
                    "id": program_id,
                    "name": program_name,
                    "cycle": cycle,
                    "faculties": faculties,
                    "campuses": [],
                    "url": PROGRAM_URL.format(main_program_id, fac_code)
                }

                yield response.follow(COURSES_LIST_URL.format(sub_traject_id, main_program_id, fac_code),
                                      self.parse_courses, cb_kwargs={'base_dict': base_dict})

    @staticmethod
    def parse_courses(response, base_dict):

        # Could have been used if everything was not only in the xhr
        # Avoid course that precede an enumeration (e.g. choice between several courses)
        # print(response.xpath("//tr[not(following-sibling::tr[1]//li and child::td/a)]//a").getall())
        courses = []
        ects = []
        for course_dict in response.json():
            courses += [str(course_dict["OPLEIDINGSONDERDEELID"])]
            ects += [int(float(course_dict["STUDIEPUNTEN"]))]

        base_dict["courses"] = courses
        base_dict["ects"] = ects

        yield base_dict
