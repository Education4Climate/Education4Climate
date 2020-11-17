import os,sys
sys.path.append(os.getcwd())
from crawl.config.driver import Driver
import time
import re
import json

prog_path = "data/crawling-results/ucl_programs_2020.json"
course_path = "data/crawling-results/ucl_courses_2020.json"
programs={}
courses={}

# mapping : [prerequisite,theme,goal,content,method,evaluation other, resources,biblio,faculty,anacs,shortname,class,location,teachers,language]
def get_program_infos(href,driver):

    infos={"href":href,"courses":[]}
    driver.get(href)
    programme_code=driver.find_element_by_class_name("abbreviation").text
    infos["name"]=driver.find_element_by_tag_name("h1").text
    infos["shortname"]=programme_code
    hrefs_elems=[e.get_attribute("href") for e in driver.find_elements_by_xpath("//a[contains(@href,'{}')]".format(programme_code.lower()))]

    # if there is a program per field
    if sum([h.endswith("-ppm") for h in hrefs_elems]) >0:
        course_prog_href=[h for h in hrefs_elems if h.endswith("-ppm")][0]
        driver.get(course_prog_href)
        courses_hrefs=[e.get_attribute("href") for e in driver.find_elements_by_xpath("//a[contains(@href,'cours-2020')]")]
        infos["courses"]=[get_course_page_infos(ref,driver) for ref in courses_hrefs]
    #if there is a tronc commun programme + specialisation
    elif sum([(re.search("([0-9]{3})t$", h) is not None) for h in hrefs_elems ])>0:
        course_prog_href=[h for h in hrefs_elems if re.search("([0-9]{3})t$", h) is not None][0]
        test=re.search("([0-9]{3})t$", course_prog_href).group(0)
        driver.get(course_prog_href)
        courses_hrefs=[e.get_attribute("href") for e in driver.find_elements_by_xpath("//a[contains(@href,'cours-2020')]")]
        infos["courses"]=[get_course_page_infos(ref,driver) for ref in courses_hrefs]
        if sum([h.endswith(test.replace("t","s")) for h in hrefs_elems]) > 0:
            course_prog_href = [h for h in hrefs_elems if h.endswith(test.replace("t","s"))][0]
            driver.get(course_prog_href)
            courses_hrefs=[e.get_attribute("href") for e in driver.find_elements_by_xpath("//a[contains(@href,'cours-2020')]")]
            infos["courses"].extend([get_course_page_infos(ref,driver) for ref in courses_hrefs])
    elif sum([h.endswith("generale$") for h in hrefs_elems ])>0:
        course_prog_href=[h for h in hrefs_elems if h.endswith("generale")][0]
        driver.get(course_prog_href)
        courses_hrefs=[e.get_attribute("href") for e in driver.find_elements_by_xpath("//a[contains(@href,'cours-2020')]")]
        infos["courses"]=[get_course_page_infos(ref,driver) for ref in courses_hrefs]
    return infos


def get_course_page_infos(href,driver):
    infos={"url":href}
    driver.get(href)

    infos["anacs"]=driver.find_element_by_class_name("anacs").text
    infos["shortname"]=driver.find_element_by_class_name("abbreviation").text
    infos["class"]=driver.find_element_by_tag_name("h1").text
    try:
        infos["location"]=driver.find_element_by_class_name("location").text
    except Exception as e:
        print(e)
    s1 = driver.find_elements_by_xpath("//div[contains(@class,'fa_cell_1')]")
    s2 = driver.find_elements_by_xpath("//div[contains(@class,'fa_cell_2')]")
    for k,v in zip(s1,s2):
        key=k.text
        value=v.text
        if "enseignant" in key.lower(): infos["teachers"]=value.split(";")
        elif "langue" in key.lower() : infos["language"]=value.lower()
        elif "contenu" in key.lower() : infos["content"]=value
        elif "thèmes" in key.lower() : infos["theme"]=value
        elif "acquis" in key.lower() : infos["goal"]=value
        elif "méthode" in key.lower() : infos["method"]=value
        elif "faculté" in key.lower() : infos["faculty"]=value
        elif "biblio" in key.lower() : infos["bibliography"]=value
        elif "ressources" in key.lower() : infos["resources"]=value
    return infos


def get_programs_from_faculty(faculty,fac_url,driver):
    driver.get(fac_url)
    elems=driver.find_elements_by_xpath("//ul[contains(@class,'ppe_liste list-group')]")
    programs=[]
    for e in elems:
        for prog in e.find_elements_by_tag_name("a"):
            p={"faculty":faculty,"url":prog.get_attribute("href"),"name":prog.text}
            p["code"]=re.search("[^-]+$",p["url"]).group().upper()
            programs.append(p)
            
    return programs


if __name__ == "__main__":
    import progressbar
    ucl_driver = Driver()
    ucl_driver.init()
    url_ucl="https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-2020.html"


    print("already crawled : {} programs, {} courses\n ".format(len(programs.keys()),len(courses.keys())))

    #Get faculties
    ucl_driver.driver.get(url_ucl)
    faculties={e.text:e.get_attribute("href") for e in ucl_driver.driver.find_elements_by_xpath("//a[contains(@class,'first')]")}

    for f,f_url in faculties.items():
        progs=get_programs_from_faculty(f,f_url,ucl_driver.driver)
        for p in progs :
            if p["code"] not in programs.keys():
                programs[p["code"]]=p
    print(len(programs.values()))
    programs={k:v for k,v in programs.items() if "bachelier" in v["name"].lower() or "master" in v["name"].lower() or "mineur" in v["name"].lower()}
    print("after cleaning : ",len(programs.keys()))
    for i,program in enumerate(programs.values()):
        infos=get_program_infos(program["url"],ucl_driver.driver)
        print("{}  {} : {} courses".format(i,program["name"],len(infos["courses"])))
        for course in infos["courses"]:
            try:
                courses[course["shortname"]]=course
            except Exception as e:
                print(e,print(course))
        program["courses"]=[c["shortname"] for c in infos["courses"]]



    json.dump(programs, open(prog_path, "w"))
    json.dump(courses, open(course_path, "w"))