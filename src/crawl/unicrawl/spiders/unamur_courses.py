# -*- coding: utf-8 -*-

import os
import sys
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

import config.utils as u
from config.settings import YEAR

sys.path.append(os.getcwd())

BASE_URl = "https://directory.unamur.be/teaching/courses/{}/{}"  # first format is code course, second is year
PROG_DATA_PATH = Path(f'../../data/crawling-output/unamur_programs_{YEAR}.json')


class UNamurCourseSpider(scrapy.Spider, ABC):
    name = "unamur-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/unamur_courses_{YEAR}.json',
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URl.format(course_id, YEAR), self.parse_main)
            break

    @staticmethod
    def parse_main(response):
        name_and_id = u.cleanup(response.css("h1::text").get())
        name = name_and_id.split("[")[0]
        id = name_and_id.split("[")[1].strip("]")

        years = u.cleanup(response.xpath("//div[@class='foretitle']").get()).strip("Cours ")
        # TODO: do we keep the 'suppléant'?
        teachers = u.cleanup(response.xpath("//div[contains(text(), 'Enseignant')]/a").getall())

        # TODO: cours en plusieurs langues?
        languages = u.cleanup(response.xpath("//div[contains(text(), 'Langue')]").getall())
        languages = [lang.split(": ")[1] for lang in languages]
        # TODO: check all langagae used
        languages_code = {"Français": 'fr',
                          "Anglais / English": 'en',
                          "Allemand / Deutsch": 'de',
                          "Néerlandais / Nederlands": 'nl',
                          "Italien": "it",
                          "Espagnol / Español": "es"}
        languages = [languages_code[lang] for lang in languages]

        # TODO: too much content selected?
        content = u.cleanup(response.xpath("//div[@class='tab-content']").get())

        cycle_ects = u.cleanup(response.xpath("//div[@id='tab-studies']/table/tbody//td").getall())
        cycles = []
        ects = []
        programs = []
        for i, el in enumerate(cycle_ects):
            if i % 3 == 0:
                programs += [el]
                if "Bachelier" in el:
                    cycles += ["bachelier"]
                elif "Master" in el:
                    cycles += ["Master"]
                else:
                    cycles += [el]
            elif i % 3 == 2:
                ects += [int(el)]

        # TODO: need to check if there are not sometimes several campuses or faculties
        organisation = response.xpath("//div[@id='tab-practical-organisation']").get()
        campus = ''
        if "Lieu de l'activité" in organisation:
            campus = u.cleanup(
                organisation.split("Lieu de l'activité")[1].split("Faculté organisatrice")[0])
        faculty = u.cleanup(organisation.split("Faculté organisatrice")[1].split("<br>")[0])

        data = {
            'name': name,
            'id': id,
            'year': years,
            'teacher': teachers,
            'language': languages,
            'cycle': cycles,
            'ects': ects,
            'content': content,
            'url': response.url,
            'faculty': faculty,
            'campus': campus,
            'program': programs
        }
        yield data

# Suppression du launcher artisanal, il ne faut pas utiliser ce genre de méthode ultra-roots...
# (il n'utilise alors pas le paramétrage du scraper)
# Pour lancer un crawler et le debugger sous Pycharm :
# Run / Edit configurations
# Choisir la configuration à modifier
# Switcher "Script path" par "Module name" et écrire : scrapy.cmdline
# Parameters : runspider unicrawl/spiders/{nom du script.py}
# Working directory : {chemin absolu de votre dossier unicrawl}\src\crawl
