# -*- coding: utf-8 -*-

import os, sys

sys.path.append(os.getcwd())
from crawl.driver import Driver

import time
import re
import json
import progressbar

# mapping : [prerequisite,theme,goal,content,method,evaluation other, resources,biblio,faculty,anacs,shortname,class,location, teachers,language]
def get_course_infos(href, driver):
    infos = {"url": href}
    # if get anac 2020-2021
    try:
        anac = driver.find_element_by_xpath("//div[contains(@class,'prgNavItem off')]")
        if anac.text == "2020-2021":
            infos["anacs"] = anac.text
            driver.get(anac.find_element_by_tag_name("a").get_attribute("href"))
            time.sleep(1)
    except Exception as e:
        infos["anacs"] = driver.find_element_by_xpath("//div[contains(@class,'prgNavItem on')]").text
        print(e)
    # else

    # technical details
    try:
        fiche = driver.find_element_by_class_name("fiche-technique")
        for element in fiche.find_elements_by_xpath("//div[contains(@class,'fiche-technique__colonne')]"):
            if "titulaire" in element.find_element_by_tag_name("h3").text.lower():
                infos["teachers"] = re.split(", | et ",
                                             element.text.replace(element.find_element_by_tag_name("h3").text, ""))
            elif "crédit" in element.find_element_by_tag_name("h3").text.lower():
                infos["credits"] = element.find_element_by_tag_name("p").text.lower()
            elif "langue" in element.find_element_by_tag_name("h3").text.lower():
                infos["language"] = element.find_element_by_tag_name("p").text.lower()
    except Exception as e:
        print(e)
        print(infos["url"])

    # textual information
    paragraphs = driver.find_elements_by_class_name("paragraphe--1")
    for paragraph in paragraphs:
        title = paragraph.find_element_by_tag_name("h2").text.lower()
        if True in [word in title for word in ["contenu", "content"]]:
            infos["content"] = paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("pr[ée][- ]?requi", title) is not None:
            infos["prerquisite"] = paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("objectif", title) is not None:
            infos["goal"] = paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("autres", title) is not None:
            infos["other"] = paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("m[ée]thode", title) is not None:
            infos["method"] = paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("[eé]valuation", title) is not None:
            infos["evaluation"] = paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text

    return infos


if __name__ == "__main__":
    ugent_driver = Driver()
    ugent_driver.init()

    # Extract courses (e.g. 'CLAS-B156') and programs (e.g. 'Master') ALREADY crawled -------------------------------
    program_fh = open("data/crawling-results/ugent_programs.json")
    courses_fh = open("data/crawling-results/ugent_courses.json")
    courses = {e["shortname"]: e for e in [json.loads(line) for line in courses_fh.readlines()]}
    programs = {e["shortname"]: e for e in [json.loads(line) for line in program_fh.readlines()]}
    program_fh.close()
    courses_fh.close()
    print("already crawled : {} programs, {} courses\n ".format(len(programs.keys()), len(courses.keys())))


    program_fh = open("data/crawling-results/ugent_programs.json", "a")
    courses_fh = open("data/crawling-results/ugent_courses.json", "a")

    # Collecting Bachelor programms list ------------------------------------------------------------------
    ugent_driver.driver.get(
        'https://studiegids.ugent.be/2020/EN/FACULTY/faculteiten.html')
    time.sleep(5) # Is it necessary?
    # HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    programs_ref = ugent_driver.driver.find_elements_by_xpath("//div[contains(@class,'search-result__result-item')]")

    for element in programs_ref:
        prg = {}
        prg["name"] = element.find_element_by_tag_name("strong").text
        prg["url"] = element.find_element_by_class_name("item-title__element_title").get_attribute("href")
        prg["faculty"] = element.find_element_by_class_name("item-title__element_title").text
        prg["code"] = element.find_element_by_class_name("search-result__mnemonique").text
        prg["location"] = element.find_element_by_class_name("search-result-formation__separator").text
        programs[prg["code"]] = prg
    print("number of bachelors to crawl : %s\n" % len(programs.keys()))
    BA_ = len(programs.keys())

    # Collecting Master programms list ----------------------------------------------------------------------
    ugent_driver.driver.get(
        "https://www.ugent.be/servlet/search?l=0&beanKey=beanKeyRechercheFormation&&types=formation&typeFo=MA&s=FACULTE_ASC&limit=200&page=1")
    time.sleep(5)
    programs_ref = ugent_driver.driver.find_elements_by_xpath("//div[contains(@class,'search-result__result-item')]")
    for element in programs_ref:
        prg = {}
        prg["name"] = element.find_element_by_tag_name("strong").text
        prg["url"] = element.find_element_by_class_name("item-title__element_title").get_attribute("href")
        prg["faculty"] = element.find_element_by_class_name("item-title__element_title").text
        prg["code"] = element.find_element_by_class_name("search-result__mnemonique").text
        prg["location"] = element.find_element_by_class_name("search-result-formation__separator").text
        programs[prg["code"]] = prg


    print("number of masters to crawl : %s\n" % (len(programs.keys()) - BA_))
    print("number of total programs to crawl : %s\n" % len(programs.keys()))


    # Browsing all programs -----------------------------------------------------------------------
    for prog_id, prg in programs.items():
        ugent_driver.driver.get(prg["url"] + "#programme")
        prg["courses"] = []
        time.sleep(5)
        print(prg["name"], prg["url"])
        # Listing all courses of the program
        courses_refs = ugent_driver.driver.find_elements_by_xpath("//a[contains(@title,'COURS')]")
        courses_refs = [e.get_attribute("href") for e in courses_refs]
        print(len(courses_refs))
        bar = progressbar.ProgressBar(maxval=len(courses_refs),
                                      widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        i = 0
        bar.start()
        # Browsing all courses
        for href in courses_refs:
            ugent_driver.driver.get(href)
            time.sleep(5)
            id_ = ugent_driver.driver.find_element_by_class_name("mnemonique").text
            prg["courses"].append(id_)
            # Getting and writing course infos
            if id_ not in courses.keys():
                infos = get_course_infos(href, ugent_driver.driver)
                infos["shortname"] = id_
                courses_fh.write(json.dumps(infos))
                courses_fh.write("\n")
                courses_fh.flush()
                courses[id_] = infos
            i += 1
            bar.update(i)
        if prg["code"] not in programs.keys():
            programs[prg["code"]] = prg
            program_fh.write(json.dumps(prg))
            program_fh.write("\n")
            program_fh.flush()
        bar.finish()
    # json.dump(programs,open("data/crawling-results/ugent_programs.json","w"))
    # json.dump(courses,open("data/crawling-results/ugent_courses.json","w"))
    ugent_driver.delete_driver()
    courses_fh.close()
    program_fh.close()