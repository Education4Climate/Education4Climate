# -*- coding: utf-8 -*-
import time

import src.crawl.unicrawl.spiders.config.settings as s
from src.crawl.unicrawl.spiders.config.driver import Driver

UGENT_URL = f"https://studiegids.ugent.be/{s.YEAR}/EN/FACULTY/faculteiten.html"

program_urls = {"Bachelor": "BACH/BACH.html", "Master": "MABA/MABA.html"}

ugent_driver = Driver()
ugent_driver.init()

# Collecting Bachelor programms list ------------------------------------------------------------------
ugent_driver.driver.get(UGENT_URL)
time.sleep(5)  # Is it necessary?

faculties_ref = [my_elem.get_attribute("href") for my_elem in
                ugent_driver.driver.find_elements_by_xpath("//aside//li[a[@target='_top']]/a")]

for fac in faculties_ref: # e.g. Click on "Faculty of Arts and Philosopy"
    ugent_driver.driver.get(fac + "/opleidingstypes.html")
    time.sleep(5)
    faculty = {}
    faculty["name"] = ugent_driver.driver.find_elements_by_class_name("faculteit")[0].text
    faculty["year"] = ugent_driver.driver.find_elements_by_class_name("faculteit")[1].text

    for _, prog_url in program_urls.items(): # Click on "Bachelor"/"Master"
        ugent_driver.driver.get(fac + "/" + prog_url)
        formation_refs = [form.get_attribute("href")
                          for form in ugent_driver.driver.find_elements_by_css_selector("a[target='_top']")]
        for ref in formation_refs: # Click on "Bachelor of Arts in Archeology"
            ugent_driver.driver.get(ref)

programs[prg["code"]] = prg # ???????????
time.sleep(5)  # Is it necessary?