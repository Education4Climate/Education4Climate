import os,sys
sys.path.append(os.getcwd())
from crawl.driver import Driver
import time
import re
import json
# mapping : [prerequisite,theme,goal,content,method,evaluation other, resources,biblio,faculty,anacs,shortname,class,location, teachers,language]
def get_course_infos(href,driver):
    infos={"url":href}
    #driver.get(href)
    infos["anacs"] = driver.find_element_by_xpath("//div[contains(@class,'prgNavItem on')]").text
    #technical details
    fiche=driver.find_element_by_class_name("fiche-technique")
    for element in fiche.find_elements_by_xpath("//div[contains(@class,'fiche-technique__colonne')]"):
        if "titulaire" in element.find_element_by_tag_name("h3").text.lower() :
            infos["teachers"]=element.text.replace(element.find_element_by_tag_name("h3").text,"").lower().split(",")
        elif "crédit" in element.find_element_by_tag_name("h3").text.lower() :
            infos["credits"]=element.find_element_by_tag_name("p").text.lower().split(",")
        elif "langue" in element.find_element_by_tag_name("h3").text.lower() :
            infos["language"]=element.find_element_by_tag_name("p").text.lower().split(",")


    #textual information
    paragraphs = driver.find_elements_by_class_name("paragraphe--1")
    for paragraph in paragraphs:
        title=paragraph.find_element_by_tag_name("h2").text.lower()
        if True in [word in title for word in ["contenu"]]:
            infos["content"]=paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("pr[ée][- ]?requi",title) is not None:
            infos["prerquisite"]=paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("objectif",title) is not None:
            infos["goal"]=paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("autres",title) is not None:
            infos["other"]=paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("m[ée]thode",title) is not None:
            infos["method"]=paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text
        elif re.search("[eé]valuation",title) is not None:
            infos["evaluation"]=paragraph.find_element_by_xpath("//div[contains(@class,'paragraphe__contenu')]").text

    return infos

if __name__ == "__main__":
    ulb_driver = Driver()
    ulb_driver.init()

    programs = {}
    courses = {}
    #Get Master programms
    #ulb_driver.driver.get("https://www.ulb.be/servlet/search?l=0&beanKey=beanKeyRechercheFormation&&types=formation&typeFo=MA&s=FACULTE_ASC&limit=200&page=1")


    #Get Bac programms
    ulb_driver.driver.get("https://www.ulb.be/servlet/search?l=0&beanKey=beanKeyRechercheFormation&&types=formation&typeFo=BA&s=FACULTE_ASC&limit=300&page=1")

    programs_ref=ulb_driver.driver.find_elements_by_xpath("//div[contains(@class,'search-result__result-item')]")
    already_processed=set()
    for element in programs_ref[:1]:
        prg={}
        prg["name"]=element.find_element_by_tag_name("strong").text
        prg["url"]=element.find_element_by_class_name("item-title__element_title").get_attribute("href")
        prg["faculty"]=element.find_element_by_class_name("item-title__element_title").text
        prg["code"]=element.find_element_by_xpath("//span[contains(@class,'mnemonique')]").text
        prg["location"]=element.find_element_by_xpath("//div[contains(@class,'__campus')]").text
        ulb_driver.driver.get(prg["url"]+"#programme")
        prg["courses"]=[]
        time.sleep(2)
        print(prg["name"],prg["url"])
        courses_refs = ulb_driver.driver.find_elements_by_xpath("//a[contains(@title,'COURS')]")
        courses_refs=[e.get_attribute("href") for e in courses_refs]
        print(len(courses_refs))
        for href in courses_refs:
            ulb_driver.driver.get(href)
            time.sleep(2)
            id_ = ulb_driver.driver.find_element_by_class_name("mnemonique").text
            prg["courses"].append(id_)
            print(id_)
            if id_ not in already_processed:
                already_processed.add(id_)
                infos =get_course_infos(href,ulb_driver.driver)
                infos["shortname"]=id_
                courses[id_]=infos
        programs[prg["code"]]=prg
    json.dump(programs,open("data/crawling-results/ulb_programs.json","w"))
    json.dump(courses,open("data/crawling-results/ulb_courses.json","w"))
    ulb_driver.delete_driver()
