from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

# warning: important to keep anchor as last argument
BASE_URL = 'https://caliweb.vub.be/?page=course-offer&id={}' + f'&year={YEAR}' + '&anchor=1'
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}vub_programs_{YEAR}.json')
LANGUAGE_DICT = {
    "Dutch": 'nl',
    "Nederlands": 'nl',
    "English": 'en',
    "Engels": 'en',
    "French": 'fr',
    "Frans": 'fr',
    "Italiaans": 'it',
    "Duits": 'de',
    'Spaans': 'es'
}

# Note: need to change the parameter ROBOTS_OBEY in the crawler settings.py to make the crawler work


class VUBCourseSpider(scrapy.Spider, ABC):
    name = "vub-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}vub_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        # TODO: normallly there can be two versions of the same class,
        #  to be checked if it's necessary to crawl both pages
        #  + can also lead to errors if the course is only find in anchor=2
        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            yield scrapy.Request(BASE_URL.format(course_id), self.parse_course,
                                 cb_kwargs={"course_id": str(course_id)})

    def parse_course(self, response, course_id):

        course_name = response.xpath("//h1/text()").get()
        # Some time the course is found at anchor=2, or 3
        if course_name is None:
            anchor = int(response.url.split("anchor=")[1])
            if anchor > 3:  # T avoid an infinite recursive call, stop at anchor 3 and return an quasi-empty entry
                yield {
                    "id": course_id, "name": '', "year": f"{YEAR}-{int(YEAR)+1}",
                    "languages": [], "teachers": [], "url": response.url,
                    "content": '', "goal": '', "activity": '', "other": ''
                }
            url = response.url.strip(str(anchor)) + str(anchor+1)
            yield scrapy.Request(url, self.parse_course, cb_kwargs={"course_id": course_id})
            return

        languages = response.xpath("//dt[contains(text(), 'Onderwijsta') or text()='Taught in']"
                                   "/following::dd[1]/text()").get()
        if languages is None or len(languages) == 0:
            languages = ['nl']
        else:
            languages = [LANGUAGE_DICT[lang] for lang in languages.split(", ")]

        teachers = response.xpath("//dt[text()='Onderwijsteam' or text()='Educational team']/following::dd[1]").get()
        teachers = teachers.strip('<dd>').strip("</dd>")
        teachers = teachers.replace("(titularis)\n", '').replace("(course titular)\n", '')
        teachers = [teacher.strip(" ").strip("\n") for teacher in teachers.split("<br>")]
        teachers = [t.lower().title() for t in teachers if t != "Promotor ."]
        # Put surname first
        teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]

        # Course description
        def get_sections_text(sections_names):
            texts = [cleanup(response.xpath(f"//dt[text()=\"{section}\"]/following::dd[1]").get())
                     for section in sections_names]
            return "\n".join(texts).strip("\n /")
        content = get_sections_text(["Course content", "Inhoud"])
        goal = get_sections_text(["Learning outcomes", "Leerresultaten"])
        other = get_sections_text(["Additional info", "Bijkomende info"])

        yield {
            "id": course_id,
            "name": course_name,
            "year": f"{YEAR}-{int(YEAR)+1}",
            "languages": languages,
            "teachers": teachers,
            "url": response.url,
            "content": content,
            "goal": goal,
            "activity": '',
            "other": other
        }

