# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy
import itertools

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URl = f"https://plus.ecam.be/public/fiche/{YEAR}/" + "{}"  # format is code course
MIC_URL = f"https://www.ecam.be/wp-content/uploads/2021/03/" + "{}.html"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}ecam_programs_{YEAR}.json')

LANGUAGES_DICT = {
    "FR": 'fr',
    "EN": 'en',
    "NL": 'nl'
}


class ECAMCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for ECAM Bruxelles
    """

    name = "ecam-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ecam_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))[["id", "courses"]].set_index("id")

        if 'MIC' in courses_ids.columns:
            mic_courses = courses_ids.loc['MIC']['courses']
            for course_id in mic_courses:
                yield scrapy.Request(
                    url=MIC_URL.format(course_id),
                    callback=self.parse_course,
                    cb_kwargs={"course_id": course_id,
                               "mic": True}
                )

        other_courses = sorted(list(set(courses_ids[courses_ids.index != 'MIC']['courses'].sum())))

        for course_id in other_courses:
            yield scrapy.Request(
                url=BASE_URl.format(course_id), 
                callback=self.parse_course, 
                cb_kwargs={"course_id": course_id,
                           "mic": False}
            )

    @staticmethod
    def parse_course(response, course_id, mic):

        name = response.xpath("//th[text()=\"Nom de l'UE\"]/following::td[1]/text()").get()
        name = " ".join(name.split(" ")[1:]) if name else ""

        # TODO
        teachers = [response.xpath("//th[text()=\"Responsable\"]/following::td[1]/text()").get()]
        teachers += response.xpath("//h5[text()='Activités organisées']/following::table[1]//tr/td[5]/text()").getall()
        teachers = [t for t in teachers if t is not None]
        teachers = list(itertools.chain.from_iterable([t.split(", ") for t in teachers]))
        teachers = list(set([t.title() for t in teachers if 'Inconnu' not in t and 'ENS' not in t]))
        if mic:
            # Put family name first
            teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]

        languages = response.xpath("//th[text()=\"Langue\"]/following::td[1]/text()").get()
        languages = languages.split(" ") if languages else ["FR"]
        languages = [LANGUAGES_DICT[lang] for lang in languages]
        languages = ["fr"] if len(languages) == 0 else languages

        # Since the content is not contained in an easily xpath-accessible div and is 
        # a combination of any number of ul, il, and p sibling elements, the 'easiest' and most elegant
        # approach is to select all the content between two consecutive section titles of interest
        xp_query = "".join([
            # let's break it down because it's relatively dense
            '//h5[contains(., \"{section}\")]',  # first, navigate to the target section title
            '/following-sibling::h5[1]',  # from there, navigate to the next section title
            '/preceding-sibling::*[preceding-sibling::h5[contains(., \"{section}\")]]' # finally, select all elements that follow the target section and precede the next section
        ])

        def get_section_text(section_name):
            texts = cleanup(response.xpath(xp_query.format(section=section_name)).xpath('string(.)').getall())
            return "\n".join(texts).strip("\n")

        content = get_section_text("Description du contenu")
        goal = get_section_text("Acquis")
        activity = get_section_text("Méthodes d'enseignement")

        yield {
            'id': course_id,
            'name': name,
            'year': f"{YEAR}-{YEAR+1-2000}",
            'languages': languages,
            'teachers': teachers,
            'url': response.url,
            'content': content,
            'goal': goal,
            'activity': activity,
            'other': ''
        }
