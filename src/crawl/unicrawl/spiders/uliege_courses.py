import argparse
import os
import sys
from abc import ABC

import numpy as np
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess

import config.utils as u
from config.driver import Driver
from config.settings import YEAR

sys.path.append(os.getcwd())


def get_courses():
    """
    Return a DataFrame containing all courses from ULiege with Code, Name, Language and web page link.
    """

    ulg_driver = Driver()
    ulg_driver.init()
    # Open search page
    ulg_driver.driver.get("https://www.programmes.uliege.be/cocoon/recherche.html")
    # Click on 'Rechercher une unité d'enseignement' tab
    ulg_driver.driver.find_elements_by_xpath("//a[contains(@href,'#unite')]")[0].click()
    # Find buttons and click on the 'Rechercher une unité d'enseignement' one
    buttons = ulg_driver.driver.find_elements_by_xpath("//button[@type='submit']")
    button = np.array(buttons)[
        [button.text == "Rechercher une unité d'enseignement" for button in buttons]
    ][0]
    button.click()

    # Browse list of courses
    courses = ulg_driver.driver.find_elements_by_xpath("//tbody//tr")
    courses_df = pd.DataFrame(index=range(len(courses)), columns=["code", "url"])
    for i, course in enumerate(courses):
        if i % 100 == 0:
            print(i, course)
        elements = course.find_elements_by_class_name("u-courses-results__row__cell")
        courses_df.loc[i, "code"] = elements[0].text
        # courses_df.loc[i, "Langue"] = elements[1].text
        # title = course.find_element_by_class_name("u-courses-results__row__cell--title")
        # courses_df.loc[i, "Intitulé"] = title.text
        link = course.find_element_by_class_name("u-courses-results__row__cell--link") \
            .find_element_by_css_selector("a").get_attribute('href')
        courses_df.loc[i, "url"] = link
    ulg_driver.delete_driver()

    return courses_df


class ULiegeSpider(scrapy.Spider, ABC):
    name = "uliege-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/uliege_courses_{YEAR}.json',
    }

    def __init__(self, *args, **kwargs):
        self.myurls = kwargs.get('myurls', [])
        super(ULiegeSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.myurls:
            yield scrapy.Request(url, self.parse_main)

    def parse_main(self, response):

        class_name = u.cleanup(response.css("h1::text").get())
        year_and_short_name = u.cleanup(
            response.xpath("//div[@class='u-courses-header__headline']/text()")
            .get()).strip(" ").split("/")
        short_name = year_and_short_name[1].strip(" ")
        years = year_and_short_name[0]

        # Get teachers name (not an easy task because not a constant syntax)
        teachers_para = response.xpath(".//section[h3[contains(text(),'Enseignant')]]/p")
        # Check first if there are links (to teachers page)
        teachers_links = teachers_para.xpath(".//a").getall()
        if len(teachers_links) == 0:
            teachers = u.cleanup(teachers_para.getall())
        else:
            teachers = u.cleanup(teachers_links)

        # Language
        languages = u.cleanup(response.xpath(".//section[h3[contains(text(), "
                                             "\"Langue(s) de l'unité d'enseignement\")]]/p").getall())
        languages_code = {"Langue française": 'fr',
                          "Langue anglaise": 'en',
                          "Langue allemande": 'de',
                          "Langue néerlandaise": 'nl',
                          "Langue italienne": "it",
                          "Langue espagnole": "es"}
        languages = [languages_code[lang] for lang in languages]

        # Content of the class
        content = u.cleanup(response.xpath(".//section[h3[contains(text(), "
                                           "\"Contenus de l'unité d'enseignement\")]]").get())[35:]

        # Cycle and credits
        credit_lines = u.cleanup(
            response.xpath(".//section[h3[contains(text(), 'Nombre de crédits')]]"
                           "//tr/td[@class='u-courses-results__row__cell--list']").getall())
        cycles = []
        ects = []
        programs = []
        for i, el in enumerate(credit_lines):
            # Program name
            if i % 2 == 0:
                programs += [el]
                if 'Master' in el:
                    cycles += ["master"]
                elif 'Bachelier' in el:
                    cycles += ["bachelier"]
                elif 'Erasmus' in el:
                    cycles += ["erasmus"]
                else:
                    cycles += [el]
            # Credit number
            else:
                ects += [int(el.split(" ")[0])]

        data = {
            'name': class_name,
            'id': short_name,
            'year': years,
            'teacher': teachers,
            'language': languages,
            'cycle': cycles,
            'ects': ects,
            'content': content,
            'url': response.url,
            'faculty': '',
            'campus': '',
            'program': programs
        }

        # The links to the programs are written in a relative manner
        program_links = response.xpath(".//section[h3[contains(text(), 'Nombre de crédits')]]"
                                       "//tr/td[@class='u-courses-results__row__cell--link']/a/@href").getall()
        data['programlinks'] = program_links
        if len(program_links) != 0:

            for link in program_links:
                yield response.follow(link, callback=self.parse_faculty_and_campus, meta=data,
                                      dont_filter=True)
        else:
            yield data

    @staticmethod
    def parse_faculty_and_campus(response):
        data = response.meta
        # Campus
        data['campus'] = u.cleanup(
            response.xpath("//li[svg[@class='u-icon icon-icons-worldmap']]").get())

        # Faculty
        faculty_link = u.cleanup(response.xpath("//ul[@class='u-courses-sidebar__list--links']"
                                                "//li/a[@class='u-link' and "
                                                "contains(text(), 'La Faculté')]/@href").get())
        # Convert address to faculty
        faculty_dict = {"archi": "Faculté d'Architecture",
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
        data["faculty"] = faculty_dict[
            [key for key in faculty_dict.keys() if key in faculty_link][0]]

        keys = ['name', 'id', 'year', 'teacher', 'language', 'cycle',
                'ects', 'content', 'url', 'faculty', 'campus', 'program']
        data = {key: data[key] for key in keys}
        yield data

# Suppression du launcher artisanal, il ne faut pas utiliser ce genre de méthode ultra-roots...
# (il n'utilise alors pas le paramétrage du scraper)
# Pour lancer un crawler et le debugger sous Pycharm :
# Run / Edit configurations
# Choisir la configuration à modifier
# Switcher "Script path" par "Module name" et écrire : scrapy.cmdline
# Parameters : runspider unicrawl/spiders/{nom du script.py}
# Working directory : {chemin absolu de votre dossier unicrawl}\src\crawl
