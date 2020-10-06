# -*- coding: utf-8 -*-

# Settings

# importing required modules
import re

import utils as u
import settings as s

# Read PDF file
page_content = u.read_pdf()

# mapping : [prerequisite,theme,goal,content,method,evaluation other, resources,biblio,faculty,anacs,shortname,class,location, teachers,language]
course = {}

if s.SEPARATOR_FIRST_AND_SECOND_PART in page_content:
    part_1_main_infos = page_content[:page_content.find(s.SEPARATOR_FIRST_AND_SECOND_PART) +
                                 len(s.SEPARATOR_FIRST_AND_SECOND_PART)]

course["name"] = re.split('[()]', part_1_main_infos)[0] #TODO: Look for exceptions
course["shortname"] = re.split('[()]', part_1_main_infos)[1] #TODO: Look for exceptions

# Extract infos from part 1 of the document [credits, study_time, year] ------------------------------

# Credits
index = page_content.find('Credits')
substring = page_content[index:index+len('Credits')+ 20]
for part in re.split('[ (]', substring):
    if u.is_float(part):
        course["credits"] = float(part)
        break

# Study time
index = page_content.find('Study time')
substring = page_content[index:index+len('Study time')+ 20]
print(substring)
for part in re.split('[ (]', substring):
    if u.is_float(part):
        course["study_time"] = float(part)
        break

# Academic Year
index = page_content.find('academic year ')
substring = page_content[index:index+len('academic year ')+ 20]
course["year"] = substring[len('academic year '):len('academic year ')+9]

# ---------------------------------------------------------------------------------------------

separator = str(int(course["credits"])) + "A"
index = page_content.rindex(separator)
part_2_courses_list = page_content[len(part_1_main_infos):index]
part_3_detailed_infos = page_content[index + len(separator):]

course["part_1_main_infos"] = part_1_main_infos
course["part_2_courses_list"] = part_2_courses_list
course["part_3_detailed_infos"] = part_3_detailed_infos

# ---------------------------------------------------------------------------------------------

# Extract infos from part 2 of the document [list of formations where course is dispensed] -----------------------

course["list_formations"] = part_2_courses_list.split(separator)

# Extract infos from part 3 of the document [ ... ] -----------------------


print(course)




"""program_urls = {"Bachelor": "BACH/BACH.html", "Master": "MABA/MABA.html"}


import os
import sys

sys.path.append(os.getcwd())
from crawl.driver import Driver

import time


ugent_driver = Driver()
ugent_driver.init()

# Collecting Bachelor programms list ------------------------------------------------------------------
ugent_driver.driver.get('https://studiegids.ugent.be/2020/EN/FACULTY/faculteiten.html')
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
"""