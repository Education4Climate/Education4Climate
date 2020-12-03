import os

import pandas as pd
import numpy as np

from src.crawl.config.driver import Driver
import scrapy
from scrapy.crawler import CrawlerProcess

import config.utils as u

import argparse
import sys
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
    button = np.array(buttons)[[button.text == "Rechercher une unité d'enseignement" for button in buttons]][0]
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
        link = course.find_element_by_class_name("u-courses-results__row__cell--link")\
            .find_element_by_css_selector("a").get_attribute('href')
        courses_df.loc[i, "url"] = link
    ulg_driver.delete_driver()

    return courses_df


class ULiegeSpider(scrapy.Spider):
    name = "uliege"

    def __init__(self, *args, **kwargs):
        self.myurls = kwargs.get('myurls', [])
        super(ULiegeSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.myurls:
            yield scrapy.Request(url, self.parse)

    @staticmethod
    def parse(response):

        class_name = u.cleanup(response.css("h1::text").get())
        year_and_short_name = u.cleanup(response.xpath("//div[@class='u-courses-header__headline']/text()")
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
        credit_lines = u.cleanup(response.xpath(".//section[h3[contains(text(), 'Nombre de crédits')]]"
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
                yield response.follow(link, callback=self.parse_faculty_and_campus, meta=data, dont_filter=True)
        else:
            yield data

    def parse_faculty_and_campus(self, response):
        data = response.meta
        # Campus
        data['campus'] = u.cleanup(response.xpath("//li[svg[@class='u-icon icon-icons-worldmap']]").get())

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
        data["faculty"] = faculty_dict[[key for key in faculty_dict.keys() if key in faculty_link][0]]

        keys = ['name', 'id', 'year', 'teacher', 'language', 'cycle',
                'ects', 'content', 'url', 'faculty', 'campus', 'program']
        data = {key: data[key] for key in keys}
        yield data


def main(output):

    # Use selenium to retrieve courses
    courses_file = "../../data/crawling-output/uliege_courses.json"
    if not os.path.exists(courses_file):
        courses_df = get_courses()
        courses_df.to_json(courses_file, orient='records', indent=1)
    else:
        courses_df = pd.read_json(courses_file)

    # Scrap all courses using scrappy
    prefile = "uliege_pre.json"
    if os.path.exists(prefile):
        os.remove(prefile)
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': prefile
    })
    process.crawl(ULiegeSpider, myurls=courses_df["url"].to_list())
    process.start()  # the script will block here until the crawling is finished
    print('All done.')

    # Merge duplicates (same course but different faculty and campuses) due to the structure of the data
    courses_df = pd.read_json(prefile)
    courses_grouped = courses_df.groupby("id")
    merged_faculty = courses_grouped["faculty"].apply(list)
    merged_campus = courses_grouped["campus"].apply(list)
    courses_df = courses_df.set_index('id')
    courses_df.loc[merged_faculty.index, "faculty"] = merged_faculty
    courses_df.loc[merged_campus.index, "campus"] = merged_campus
    courses_df = courses_df.reset_index()
    courses_df = courses_df.drop_duplicates(subset=["id"])
    # Save modified file
    courses_df.to_json(output, orient="records", indent=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Craw the ULiege courses catalog.')
    parser.add_argument("--output", default="output.json", type=str, help="Output file")
    args_ = parser.parse_args()
    main(args_.output)
