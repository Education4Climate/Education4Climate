# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URl = "http://progcours.vinci.be/cocoon/cours/{}.html"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}vinci_programs_{YEAR}.json')

LANGUAGES_DICT = {
    "Langue française": 'fr',
    "Langue anglaise": 'en'
}


class VINCICourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for Haute Ecole Léonard de Vinci
    """

    name = "vinci-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}vinci_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        # Warning: COSV2430-1 leading to 500

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URl.format(course_id), self.parse_main, cb_kwargs={"course_id": course_id})

    @staticmethod
    def parse_main(response, course_id):

        course_name = response.xpath("////td[@class='LibCours']/text()").get()

        def removeRepeatedCourseNames(t):
            l=(len(t)-1)//2
            p1=t[0:l]
            p2=t[l+2:]
            p3=t[l:l+1]
            if p1==p2 and p3==',':
                return p1
            else:
                return t

        course_name = removeRepeatedCourseNames(course_name)
 
        if course_name is None:
            yield {
                "id": course_id, "name": '', "year": f"{YEAR}-{int(YEAR) + 1}",
                "languages": ["fr"], "teachers": [], "url": response.url,
                "content": '', "goal": '', "activity": '', "other": ''
            }
            
        years = response.xpath("//div[@id='TitrePrinc']/text()").get().split(" ")[-1]
        course_rubric_txt = "//div[@class='TitreRubCours' and contains(text(), \"{}\")]"

        '''
        teachers = cleanup(response.xpath(f"{course_rubric_txt.format('prof')}/following::tr[1]//a").getall())
        teachers += cleanup(response.xpath(f"{course_rubric_txt.format('Coord')}/following::tr[1]//a").getall())
        teachers = [t.replace(" ", '') for t in teachers]
        teachers = list(set(teachers))
        teachers = [" ".join(teacher.split(" ")[1:]).title() + " " + teacher.split(" ")[0].strip(" ")
                    for teacher in teachers]
        '''
        languages = response.xpath(course_rubric_txt.format("Langue(s)") + "/following::td[2]/text()").getall()
        languages = [LANGUAGES_DICT[l] for l in languages]
        languages = ["fr"] if len(languages) == 0 else languages
        
        
        teachers=[]

        def getSection(section,joinListElements=True):

                mapping={
                 'organisation' : ( 'rub_dfeorg', "Organisation et évaluation"                                                   ),
                 'content'      : ( 'rub_APER'  , "Contenus de l'unité d'enseignement"                                           ),
                 'goal'         : ( 'rub_OBJT'  , "Acquis d'apprentissage (objectifs d'apprentissage) de l'unité d'enseignement" ),
                 'prerequisites': ( 'rub_PRER'  , "Savoirs et compétences prérequis"                                             ),
                 'activity'     : ( 'rub_TRPR'  , "Activités d'apprentissage prévues et méthodes d'enseignement"                 ),
                 'medium'       : ( 'rub_ORGA'  , "Mode d'enseignement (présentiel, à distance, hybride)"                        ),
                 'readings'     : ( 'rub_NOCO'  , "Lectures recommandées ou obligatoires et notes de cours"                      ),
                 'evaluation'   : ( 'rub_EVAL'  , "Modalités d'évaluation et critères"                                           ),
                 'internship'   : ( 'rub_STAG'  , "Stage(s)"                                                                     ),
                 'remarks'      : ( 'rub_REM'   , "Remarques organisationnelles"                                                 ),
                 'teachers'     : ( 'rub_CONT'  , "Contacts"                                                                     ),
                 }
                 
                if section not in mapping.keys():
                        return []

                rub=mapping[section][0]

                tableRows=[s for s in response.xpath('//tr')]
                
                positionOfSection=[x for x,s in enumerate(tableRows) if s.xpath('./@id').get()==rub]
                if positionOfSection:
                        positionOfElementToExtract=positionOfSection[0]+1 
                        extract=[s.get() for s in tableRows[positionOfElementToExtract].xpath('td[@class="LibRubCours"]/descendant-or-self::text()')]
                        extract=[cleanup(s) for s in extract if s.strip()] # to get rid of empty lines
                        if joinListElements:
                                return '\n'.join(extract)
                        else:
                                return extract
                return []


        content=getSection('content')
        goal=getSection('goal')
        activity=getSection('activity')


        yield {
            'id': course_id,
            'name': course_name,
            'year': years,
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            "content": content,
            "goal": goal,
            "activity": activity,
            "other": ''
        }
