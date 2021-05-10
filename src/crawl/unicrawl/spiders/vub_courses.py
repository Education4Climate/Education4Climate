from abc import ABC
from pathlib import Path

import pandas as pd

import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'https://caliweb.vub.be/?page=course-offer&id={}&anchor=1'
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}vub_programs_{YEAR}.json')
LANGUAGE_DICT = {"Dutch": 'nl',
                 "Nederlands": 'nl',
                 "English": 'en',
                 "Engels": 'en',
                 "French": 'fr',
                 "Frans": 'fr',
                 "Italiaans": 'it',
                 "Duits": 'de',
                 'Spaans': 'es'}

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
            base_dict = {"id": str(course_id)}
            yield scrapy.Request(BASE_URL.format(course_id), self.parse_course, cb_kwargs={"base_dict": base_dict})

    def parse_course(self, response, base_dict):

        name = response.xpath("//h1/text()").get()
        # Some time the course is found at anchor=2, or 3
        if name is None:
            anchor = int(response.url.split("anchor=")[1])
            if anchor > 3:  # T avoid an infinite recursive call, stop at anchor 3
                return
            url = response.url.strip(str(anchor)) + str(anchor+1)
            yield scrapy.Request(url, self.parse_course, cb_kwargs={"base_dict": base_dict})
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
        teachers = [t for t in teachers if t != "Promotor ."]
        # Put surname first
        teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]

        sections = ["Course content", "Additional info", "Learning outcomes",
                    "Inhoud", "Bijkomende info", "Leerresultaten"]
        content = ""
        for section in sections:
            section_content = cleanup(response.xpath(f"//dt[text()=\"{section}\"]/following::dd[1]").get())
            content += "\n" + section_content if section_content is not None or len(section_content) != 0 else ""
        content = content.strip("\n")

        cur_dict = {"name": name,
                    "year": f"{YEAR}-{int(YEAR)+1}",
                    "languages": languages,
                    "teachers": teachers,
                    "url": response.url,
                    "content": content}

        yield {**base_dict, **cur_dict}
