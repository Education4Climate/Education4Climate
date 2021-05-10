from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://uhintra03.uhasselt.be/studiegidswww/opleidingsonderdeel.aspx?a={}&i={}&n=4&t=01"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}uhasselt_programs_{YEAR}.json')
LANGUAGE_DICT = {'Nederlands': 'nl',
                 'Engels': 'en',
                 'English': 'en'}


class UHasseltCourseSpider(scrapy.Spider, ABC):
    name = "uhasselt-courses"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}uhasselt_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_ids = pd.read_json(open(PROG_DATA_PATH, "r"))["courses"]
        courses_ids_list = sorted(list(set(courses_ids.sum())))

        for course_id in courses_ids_list:
            base_dict = {"id": str(course_id)}
            yield scrapy.Request(BASE_URL.format(YEAR, course_id), self.parse_main, cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_main(response, base_dict):

        course_name = response.xpath("//h4/text()").get().split(" (")[0]

        # Teachers are list in a very weird way (html-wise)
        teachers = response.xpath("//td[contains(text(), 'lecturer') or contains(text(), 'verantwoordelijke')]"
                                  "/following::td[1]/a/text()").getall()
        teachers_path = "//td[contains(text(), 'teaching team') or contains(text(), 'onderwijsteam')]"
        teachers += response.xpath(f"{teachers_path}/following::td[1]/a/text()").getall()
        teachers += response.xpath(f"{teachers_path}/following::tr/td/a/text()").getall()
        # Remove all the dr., ir., etc and Mevrouw and De heer
        teachers = [t.split('. ')[-1] for t in teachers]
        for text in ['Mevrouw ', 'De heer ']:
            teachers = [t.replace(text, '') for t in teachers]
        # Put surname first
        teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" for t in teachers]

        languages = response.xpath("//td[contains(text(), 'Onderwijstaal') "
                                   "or contains(text(), 'Language of instruction')]/b/text()").getall()
        languages = [LANGUAGE_DICT[lang] for lang in languages]

        content = cleanup(response.xpath("//span[text()='Inhoud' or text()='Content']//following::td[1]").get())

        cur_dict = {
            'name': course_name,
            'year': f"{YEAR}-{int(YEAR)+1}",
            'teachers': teachers,
            'languages': languages,
            'url': response.url,
            'content': content,
        }

        yield {**base_dict, **cur_dict}
