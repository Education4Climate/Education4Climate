from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER
from src.crawl.utils import cleanup

BASE_URL = f"https://studiekiezer.ugent.be/nl/zoek?zt=&aj={YEAR}" + "&loc={}"
BASE_URL_2 = "https://studiekiezer.ugent.be/nl/incrementalsearch?target=zoek&ids={}"


class UGentProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for UGent
    """

    name = 'ugent-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ugent_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        campuses = ['Gent', 'Brugge', 'Oudenaarde', 'Kortrijk']
        for campus in campuses:
            yield scrapy.Request(
                url=BASE_URL.format(campus.upper()),
                callback=self.parse_program_numbers,
                cb_kwargs={"campus": campus}
            )

    def parse_program_numbers(self, response, campus):

        program_numbers = response.xpath("//div[contains(@id, 'lazyLoadedChunk')]/@data").getall()
        for program_numbers_sublist in program_numbers:
            yield scrapy.Request(
                url=BASE_URL_2.format(program_numbers_sublist),
                callback=self.parse_main,
                cb_kwargs={"campus": campus}
            )

    def parse_main(self, response, campus):

        program_links = response.xpath("//a[h2[@class='title']]/@href").getall()
        for link in program_links:
            programma_link = "/".join(link.split("/")[:-1]) + f"/programma/{YEAR}"
            yield response.follow(programma_link, self.parse_program, cb_kwargs={'campus': campus})

    @staticmethod
    def parse_program(response, campus):

        program_id = response.xpath("//h1/@data-code").get()
        program_name = response.xpath("//h1[@id='titleLabel']/text()").get()
        # Don't keep programs for exchange students
        if "exchange proramme" in program_name.lower():
            return
        # Just a list of courses, too generic
        if "universiteitsbrede keuzevakken" in program_name.lower():
            return

        cycle = response.xpath("//i[contains(@class, 'glyphicon-education')]/following::span[1]/text()").get()
        if 'aster' in cycle:
            cycle = 'master'
        elif 'achelor' in cycle:
            if 'Bridging' in program_name or 'Brugprogramma' in program_name or\
                    'List' in program_name or 'Lisjt' in program_name or 'Ritsweg' in program_name:
                cycle = 'other'
            else:
                cycle = 'bac'
        elif 'ostgradua' in cycle:
            cycle = 'postgrad'
        elif 'octor' in cycle:
            cycle = 'doctor'
        else:
            cycle = 'other'

        # Can have several faculties
        faculties = response.xpath("//i[contains(@class, 'glyphicon-map-marker')]"
                                   "/following::div[1]//span/text()").getall()
        faculties = [faculty.strip(" \n") for faculty in faculties]

        # Course list
        div_text = "//div[div[h4[.//div[contains(text(), 'Volledig') or contains(text(), 'Full')]]]][1]"
        courses_text = "//tr[not(@class='nietaangeboden')]//td[@class='cursusnaam']"
        courses_ids = response.xpath(f"{div_text}{courses_text}//span/@title").getall()
        # courses_names = response.xpath(f"{div_text}{courses_text}//span/text()").getall()
        courses_urls = response.xpath(f"{div_text}{courses_text}//a/@ng-click").getall()
        courses_urls = [course_url.split(",")[4].strip(" '") + "/"
                        + '/'.join(course_url.split(",")[1:4]) for course_url in courses_urls]
        # ects = response.xpath(f"{div_text}//td[@class='SP']//span/text()").getall()
        # ects = [int(float(e.replace(',', '.'))) for e in ects]

        # TODO: rerun and remove duplicates
        # TODO: ugly, clean up
        courses_languages = []
        courses_names = []
        ects = []
        for course_id in courses_ids:
            courses_text_2 = f"//tr[not(@class='nietaangeboden') and td[@class='cursusnaam' and .//span[@title='{course_id}']]]"
            id_txt = f"{div_text}{courses_text}//span[@title='{course_id}']"
            id_txt_2 = f"{div_text}{courses_text_2}"
            courses_language = cleanup(response.xpath(f"{id_txt_2}//td[@class='taal']/div/div[1]").get())
            courses_languages += [courses_language] if courses_language is not None else ["nl"]
            course_name = response.xpath(f"{id_txt}/text()").get()
            courses_names += [course_name] if courses_language is not None else ['']
            e = response.xpath(f"{id_txt_2}//td[@class='SP']//span/text()").get()
            ects += [int(float(e.replace(',', '.')))] if e is not None else [0]

        yield {
            'id': program_id,
            'name': program_name,
            'cycle': cycle,
            'faculties': faculties,
            'campuses': [campus],
            'url': response.url,
            'courses': courses_ids,
            'ects': ects,
            'courses_names': courses_names,
            'courses_languages': courses_languages,
            'courses_urls': courses_urls
        }
