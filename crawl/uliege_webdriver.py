import os
from os.path import join, dirname, abspath

from crawl.driver import Driver
import time
import re
import json
import pandas as pd

import numpy as np

import sys
sys.path.append(os.getcwd())


# mapping : [prerequisite,theme,goal,content,method,evaluation other,
# resources,biblio,faculty,anacs,shortname,class,location, teachers,language]



if __name__ == "__main__":

    # Get Bac programs
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
    courses_df = pd.DataFrame(index=range(len(courses)), columns=["Code", "Intitulé", "Langue", "Link"])
    for i, course in enumerate(courses[0:10]):
        elements = course.find_elements_by_class_name("u-courses-results__row__cell")
        courses_df.loc[i, "Code"] = elements[0].text
        courses_df.loc[i, "Langue"] = elements[1].text
        title = course.find_element_by_class_name("u-courses-results__row__cell--title")
        courses_df.loc[i, "Intitulé"] = title.text
        link = course.find_element_by_class_name("u-courses-results__row__cell--link")\
            .find_element_by_css_selector("a").get_attribute('href')
        courses_df.loc[i, "Link"] = link
    ulg_driver.delete_driver()

    # TODO : Use scrappy to scrap all courses pages?


