import os

import pandas as pd
import numpy as np

from crawl.config.driver import Driver
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
    courses = ulg_driver.driver.find_elements_by_xpath("//tbody//tr")[0:10]  # TODO: remove just for testing
    courses_df = pd.DataFrame(index=range(len(courses)), columns=["Code", "Intitulé", "Langue", "Link"])
    for i, course in enumerate(courses):
        elements = course.find_elements_by_class_name("u-courses-results__row__cell")
        courses_df.loc[i, "Code"] = elements[0].text
        courses_df.loc[i, "Langue"] = elements[1].text
        title = course.find_element_by_class_name("u-courses-results__row__cell--title")
        courses_df.loc[i, "Intitulé"] = title.text
        link = course.find_element_by_class_name("u-courses-results__row__cell--link")\
            .find_element_by_css_selector("a").get_attribute('href')
        courses_df.loc[i, "Link"] = link
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
        short_name = year_and_short_name[1]
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
        for i, line in enumerate(credit_lines):
            # Cycle
            if i % 2 == 0:
                if 'Master' in line:
                    cycles += ["master"]
                elif 'Bachelier' in line:
                    cycles += ["bachelier"]
                elif 'Erasmus' in line:
                    cycles += ["erasmus"]
                else:
                    cycles += [line]
            # Credit number
            else:
                ects += [int(line.split(" ")[0])]

        data = {
            'name': class_name,
            'id': short_name,
            'years': years,
            'teachers': teachers,
            'languages': languages,
            'cycle': cycles,
            'ects': ects,
            'content': content,
            'url': response.url
        }
        yield data


def main(output):

    # Use selenium to retrieve courses
    courses_df = get_courses()

    # Scrap all courses using scrappy
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': output
    })
    process.crawl(ULiegeSpider, myurls=courses_df["Link"].to_list())
    process.start()  # the script will block here until the crawling is finished
    print('All done.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Craw the ULiege courses catalog.')
    parser.add_argument("--output", default="output.json", type=str, help="Output file")
    args_ = parser.parse_args()
    main(args_.output)
