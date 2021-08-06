# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URl = "https://www.ecam.be/{}"  # format is code course
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}ecam_programs_{YEAR}.json')

LANGUAGES_DICT = {"FR": 'fr', "EN": 'en', "NL": 'nl'}


class ECAMCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for ECAM Bruxelles
    """

    name = "ecam-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ecam_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            base_dict = {"id": course_id}

            yield scrapy.Request(
                url=BASE_URl.format(course_id), 
                callback=self.parse_course, 
                cb_kwargs={"base_dict": base_dict}
            )

    @staticmethod
    def parse_course(response, base_dict):

        name = response.xpath("//th[text()=\"Nom de l'UE\"]/following::td[1]/text()").get()
        name = " ".join(name.split(" ")[1:]) if name else ""
        years = response.css('.label.label-info').re("([0-9]{4}\-[0-9]{4})")
        years = years[0] if years else []
        teachers = response.xpath("//th[text()=\"Responsable\"]/following::td[1]/text()").get()
        if teachers:
            teachers = teachers.split(',')
            # Use format "Lastname Firstname"
            teachers = [t.split(" ", 1) for t in teachers]
            teachers = ["{} {}".format(t[1], t[0]) for t in teachers]
        else:
            teachers = []
        languages = response.xpath("//th[text()=\"Langue\"]/following::td[1]/text()").get()
        languages = languages.split(" ") if languages else ["FR"]
        languages = [LANGUAGES_DICT[lang] for lang in languages]

        # Since the content is not contained in an easily xpath-accessible div and is 
        # a combination of any number of ul, il, and p sibling elements, the 'easiest' and most elegant
        # approach is to select all the content between two consecutive section titles of interest
        sections = ["Acquis", "Description du contenu"]
        xp_query = "".join([
            # let's break it down because it's relatively dense
            '//h5[contains(., \'{section}\')]', # first, navigate to the target section title
            '/following-sibling::h5[1]', # from there, navigate to the next section title 
            '/preceding-sibling::*[preceding-sibling::h5[contains(., \'{section}\')]]' # finally, select all elements that follow the target section and precede the next section
        ])
        sections_contents = [" ".join(cleanup(response.xpath(xp_query.format(section=title)).xpath('string(.)').getall())) for title in sections]
        content = " ".join(sections_contents).strip()
        
        yield {
            'id': base_dict['id'],
            'name': name,
            'year': years,
            'teachers': teachers,
            'languages': languages,
            'content': content,
            'url': response.url,
        }
