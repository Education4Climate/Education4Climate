# -*- coding: utf-8 -*-
import scrapy
from abc import ABC
from pathlib import Path

from src.crawl.utils import cleanup
from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://web.umons.ac.be/fr/formations/"
BASE_DATA = {
    "degree[]": "bachelor",
    "schedule[]": ["daytime", "adapted", "alternate"],
    "complete": "1",
    "search": "",
    "search-trainings": "1",
}


class UMonsProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for University of Mons
    """

    name = "umons-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}umons_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        # yield scrapy.Request(url=BASE_URL, callback=self.parse_offer)

        cycle_url_codes = ["bachelor", "master", "specialization", "phd",
                           "aess", "capaes", "certificate", "interuniversity-certificate"]
        cycle_codes = ["bac", "master", "master", "doctor",
                       "other", "certificate", "certificate", "certificate"]

        for url_code, code in zip(cycle_url_codes, cycle_codes):

            BASE_DATA["degree[]"] = url_code

            # Number of results is limited to 40 and there are more than 40 master
            # So divide the search by faculty
            if url_code == "master":
                for faculty_code in ["2", "3", "5", "6", "7", "8", "9", "10", "11"]:
                    base_data_with_faculty = BASE_DATA.copy()
                    base_data_with_faculty["entity[]"] = faculty_code
                    yield scrapy.http.FormRequest(
                        BASE_URL,
                        callback=self.parse_offer,
                        formdata=base_data_with_faculty,
                        cb_kwargs={"cycle": code}
                    )
            else:
                yield scrapy.http.FormRequest(
                    BASE_URL,
                    callback=self.parse_offer,
                    formdata=BASE_DATA,
                    cb_kwargs={"cycle": code}
                )

    def parse_offer(self, response, cycle):

        program_links = response.xpath("//a[header]/@href").getall()
        for link in program_links:
            yield response.follow(link, self.parse_prog, cb_kwargs={'cycle': cycle})

    def parse_prog(self, response, cycle):

        href = response.xpath(
            '//a[contains(@class, "button-primary-alt scheme-background scheme-background-hover")]/@href').get()
        if not href:
            # No program details and no program id
            return
        else:
            campus = response.xpath('//div[div/text()="Lieu"]').css('div.value::text').get()
            if 'mailto' in href:
                # Note: this avoids an error on the 'Bachelier en Droit' and
                # 'Bachelier en Sciences Humaines et Sociales'
                #  but anyways these programs are organised by the ULB
                return
            yield response.follow(url=href, callback=self.parse_prog_detail,
                                  cb_kwargs={'campus': campus,
                                             'cycle': cycle,
                                             'url': response.url})

    @staticmethod
    def parse_prog_detail(response, campus, cycle, url):

        faculty = response.css('td.facTitle::text').get()
        program_name = response.css('td.cursusTitle::text').get().replace("  ", " ")
        if not program_name:
            return
        courses = response.css('span.linkcodeue::text').getall()
        courses = [course.strip(" ") for course in courses]
        ects = cleanup(response.xpath("//td[@class='credits colnumber']").getall())
        ects = [int(e) if e != '' else 0 for e in ects]

        yield {
            'id': response.url.split("/")[-1].split(".")[0],
            'name': program_name,
            'cycle': cycle,
            'faculties': [faculty],
            'campuses': [campus],
            'url': url,
            'courses': courses,
            'ects': ects
        }
