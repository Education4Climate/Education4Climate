from abc import ABC
from pathlib import Path
import json
import urllib.parse
import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://www.ulb.be/servlet/search?" \
           "l=0&beanKey=beanKeyRechercheFormation&&types=formation" \
           "&typeFo={}&s=FACULTE_ASC&limit=999&page=1"

PATH_PROG_URL = urllib.parse.quote('/ws/ksup/programme?gen=prod&anet={}&lang=fr&', safe='{}')
PROG_URL = f'https://www.ulb.be/api/formation?path={PATH_PROG_URL}'

PATH_SUBPROG_URL = urllib.parse.quote('/ws/ksup/programme?gen=prod&anet={}&option={}&lang=fr&', safe='{}')
SUBPROG_URL = f'https://www.ulb.be/api/formation?path={PATH_SUBPROG_URL}'


class ULBProgramSpider(scrapy.Spider, ABC):
    name = 'ulb-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ulb_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        for deg in ('BA', 'MA', 'MA60', 'MS'):
            cycle = 'bac' if deg == 'BA' else 'master'
            yield scrapy.Request(
                url=BASE_URL.format(deg),
                callback=self.parse_main,
                cb_kwargs={'cycle': cycle}
            )

    def parse_main(self, response, cycle):

        main_div = "//div[contains(@class, 'search-result__result-item')]"
        program_links = response.xpath(f"{main_div}/div[contains(@class, 'search-result__formations')]/a/@href").getall()
        campuses = response.xpath(f"{main_div}/div[contains(@class, 'search-result__campus')]/span/text()").getall()
        for link, campus in zip(program_links, campuses):
            yield scrapy.Request(
                url=link,
                callback=self.parse_secondary,
                cb_kwargs={'main_program_id': None, 'cycle': cycle, 'campus': campus.strip(" \n")}
            )

    def parse_secondary(self, response, main_program_id, cycle, campus):

        # Get subprograms if there are some
        main_div = "//div[contains(@class, 'search-result__result-item')]"
        program_links = response.xpath(
            f"{main_div}/div[contains(@class, 'search-result__formations')]/a/@href").getall()
        if len(program_links) != 0:
            campuses = response.xpath(f"{main_div}/div[contains(@class, 'search-result__campus')]/div/text()").getall()
            main_program_id = response.url.split("/")[-1].upper()
            for link, campus in zip(program_links, campuses):
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_secondary,
                    cb_kwargs={'main_program_id': main_program_id, 'campus': campus.strip(" \n"), 'cycle': cycle}
                )
            return

        # Otherwise extract information for the program
        program_id = response.url.split("/")[-1]
        program_name = response.xpath("//h1/text()").get()
        faculty = response.xpath("//div[@class='zone-titre__surtitre']/a/text()").get()
        base_dict = {'id': program_id.upper(),
                     'name': program_name,
                     'faculty': faculty,
                     'cycle': cycle,
                     'campus': campus,
                     'url': response.url}

        program_id = program_id.upper()
        if main_program_id is None:
            link = PROG_URL.format(program_id)
        else:
            link = SUBPROG_URL.format(main_program_id, program_id)
        yield scrapy.Request(url=link, callback=self.parse_programme,
                             cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_programme(response, base_dict):

        json_obj = json.loads(json.loads(response.text)['json'])

        courses_ects = []
        for bloc in json_obj['blocs']:
            if bloc['anac'] == YEAR:
                courses_ects += [(course['id'], course['credits']) for course in bloc['progCourses']]

        if len(courses_ects) == 0:
            return

        courses, ects = zip(*list(set(courses_ects)))
        base_dict['courses'] = courses
        base_dict['ects'] = ects

        yield base_dict
