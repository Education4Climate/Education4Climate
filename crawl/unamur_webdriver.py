# -*- coding: utf-8 -*-

import os, sys

sys.path.append(os.getcwd())
from crawl.driver import Driver

import numpy as np
import pandas as pd

import time
import re
import json
import progressbar
import settings as s


if __name__ == "__main__":
    unamur_driver = Driver()
    unamur_driver.init()

    unamur_driver.driver.get("https://directory.unamur.be/teaching/programmes")
    # Get all faculties
    year = 2020
    faculties = unamur_driver.driver.find_elements_by_xpath(f"//div[@id='tab-{year}']//h3/a")
    for faculty in faculties:
        faculty.click()

    # Get formation types (keep only the ones starting with Bachelier and Master)
    formation_types = unamur_driver.driver.find_elements_by_xpath(f"//div[@id='tab-{year}']//h4/a")
    formation_types = np.array(formation_types)[[f.text.startswith("Bachelier")
                                       or f.text.startswith("Master") for f in formation_types]].tolist()
    for ft in formation_types:
        ft.click()

    # Get all formations
    formations = unamur_driver.driver.find_elements_by_xpath(f"//div[@id='tab-{year}']//div//div//a")
    formations = np.array(formations)[[f.text != "" for f in formations]].tolist()

    formations_df = pd.DataFrame(index=range(len(formations)), columns=["nom", "url"])
    formations_df.nom = [f.text for f in formations]
    formations_df.url = [f.get_attribute('href') for f in formations]

    # TODO: from here we can access the list of course for each program (does not require selenium)
    #   The courses pages doesn't seem to require selenium either. -> use scrapy?

    unamur_driver.delete_driver()
