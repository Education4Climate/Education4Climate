# -*- coding: utf-8 -*-

import json
import re
import time

import progressbar

from src.crawl.unicrawl.spiders.config.driver import Driver

ULB_URL = "https://www.ulb.be/servlet/search?" \
          "l=0&beanKey=beanKeyRechercheFormation&&types=formation" \
          "&typeFo=BA&s=FACULTE_ASC&limit=300&page=1"


# mapping : [prerequisite,theme,goal,content,method,
# evaluation other, resources,biblio,faculty,anacs,shortname,class,location, teachers,language]
def get_course_infos(href, driver):
    infos = {"url": href}
    driver.get(href)
    infos["class"] = driver.find_element_by_id("zone-titre").find_element_by_tag_name("h1").text
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
            infos["content"] = paragraph.find_element_by("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("pr[ée][- ]?requi", title) is not None:
            infos["prerequisite"] = paragraph.find_element_by_xpath(
                "//div[contains(@class,'paragraphe__contenu')]").text
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
    ulb_driver = Driver()
    ulb_driver.init()

    # Extract courses (e.g. 'CLAS-B156') and programs (e.g. 'Master') ALREADY crawled -------------------------------
    program_fh = open("data/crawling-output/ulb_programs.json")
    courses_fh = open("data/crawling-output/ulb_courses.json")
    courses = {e["shortname"]: e for e in [json.loads(line) for line in courses_fh.readlines()]}
    programs_saved = {e["shortname"]: e for e in
                      [json.loads(line) for line in open("data/crawling-output/ulb_programs.json").readlines()]}

    program_fh.close()
    courses_fh.close()
    print("already crawled : {} programs, {} courses\n ".format(len(programs_saved.keys()), len(courses.keys())))

    # Get Bac programms
    ulb_driver.driver.get(ULB_URL)
    time.sleep(2)
    programs_ref = ulb_driver.driver.find_elements_by_xpath("//div[contains(@class,'search-result__result-item')]")

    for element in programs_ref:
        prg = {}
        prg["name"] = element.find_element_by_tag_name("strong").text
        prg["url"] = element.find_element_by_class_name("item-title__element_title").get_attribute("href")
        prg["faculty"] = element.find_element_by_xpath(
            "//span[contains(@class,'search-result__structure-rattachement')]").text
        # prg["faculty"]=element.find_element_by_class_name("item-title__element_title").text
        prg["code"] = element.find_element_by_class_name("search-result__mnemonique").text
        prg["location"] = element.find_element_by_class_name("search-result-formation__separator").text
        programs_saved[prg["code"]] = prg

    # Get Master programms
    ulb_driver.driver.get("https://www.ulb.be/servlet/search?l=0&beanKey=beanKeyRechercheFormation&&"
                          "types=formation&typeFo=MA&s=FACULTE_ASC&limit=200&page=1")
    time.sleep(1)
    programs_ref = ulb_driver.driver.find_elements_by_xpath("//div[contains(@class,'search-result__result-item')]")
    for element in programs_ref:
        prg = {}
        prg["name"] = element.find_element_by_tag_name("strong").text
        prg["url"] = element.find_element_by_class_name("item-title__element_title").get_attribute("href")
        prg["faculty"] = element.find_element_by_xpath(
            "//span[contains(@class,'search-result__structure-rattachement')]").text
        prg["code"] = element.find_element_by_class_name("search-result__mnemonique").text
        prg["location"] = element.find_element_by_class_name("search-result-formation__separator").text
        programs_saved[prg["code"]] = prg

    print("number of total programs to crawl : %s\n" % len(programs_saved.keys()))
    for p_id, prg in programs_saved.items():
        #        if p_id in programs_saved.keys():
        #            print(prg["name"],prg["url"],"-- already crawled")
        #            continue
        ulb_driver.driver.get(prg["url"] + "#programme")
        prg["courses"] = []
        time.sleep(2)
        print(prg["name"], prg["url"])
        courses_refs = ulb_driver.driver.find_elements_by_xpath("//a[contains(@title,'COURS')]")
        courses_refs = [e.get_attribute("href") for e in courses_refs]
        print(len(courses_refs))
        bar = progressbar.ProgressBar(maxval=len(courses_refs),
                                      widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()

        for i, href in enumerate(courses_refs):
            if not href.startswith("http"):
                print("skipping ", href)
                continue
            try:
                ulb_driver.driver.get(href)
            except Exception as e:
                print(e)
                print("restarting driver")
                ulb_driver.init()
                ulb_driver.driver.get(href)
            time.sleep(2)
            try:
                id_ = ulb_driver.driver.find_element_by_class_name("mnemonique").text
                prg["courses"].append(id_)
                if id_ not in courses.keys():
                    infos = get_course_infos(href, ulb_driver.driver)
                    infos["shortname"] = id_
                    courses_fh.write(json.dumps(infos))
                    courses_fh.write("\n")
                    courses_fh.flush()
                    courses[id_] = infos
            except Exception as e:
                print(e, href)
            bar.update(i)
        bar.finish()
        print(prg["code"], " done crawling. Saving..")
        if prg["code"] not in programs_saved.keys():
            prg["courses"] = list(set(prg["courses"]))
            programs_saved[prg["code"]] = prg
            program_fh.write(json.dumps(prg))
            program_fh.write("\n")
            program_fh.flush()
        bar.finish()
    # json.dump(programs,open("data/crawling-output/ulb_programs.json","w"))
    # json.dump(courses,open("data/crawling-output/ulb_courses.json","w"))

    ulb_driver.delete_driver()
    courses_fh.close()
    program_fh.close()
