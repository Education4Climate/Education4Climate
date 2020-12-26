# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR
from config.utils import cleanup

BASE_URL = "https://helue.azurewebsites.net/ListingPub"


class HELCourseSpider(scrapy.Spider, ABC):
    """
    Course crawler for Haute Ecole de la Ville de Liège
    """

    name = "hel-courses"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/hel_courses_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(BASE_URL, self.parse_main)

    def parse_main(self, response):

        ue_links = response.xpath("//a[@title='ouvrir cette fiche']/@href").getall()
        for link in ue_links:
            yield response.follow(link, self.parse_ue)
            break

    @staticmethod
    def parse_ue(response):
        info_par = response.xpath("//tr[@class='entete']//p").get()
        year = info_par.split("Année académique</b> : ")[1].split('<br>')[0]
        faculty = info_par.split("Département</b> : ")[1].split('<br>')[0]
        program = info_par.split("Cursus</b> : ")[1].split('<br>')[0]
        ects = info_par.split("Nombre de crédits</b> : ")[1].split('<br>')[0]
        campus = info_par.split("Implantation(s)</b> : ")[1].split('<br>')[0]
        ue_name = response.xpath("//td[@class='important_ue'and @colspan=4]/text()").get().split(": ")[1]
        ue_id = response.xpath("//td[@class='important_ue'and @colspan=2]/text()").get().strip(": ")
        cycle = response.xpath("//td[b[contains(text(), 'Cycle :')]]/text()").get().strip(" ")
        teachers = cleanup(response.xpath("//table[@class='table_aa_profs_heures']/tbody/tr/td[2]").getall())
        teachers = [t.strip(",") for t in teachers]

        # TODO: content
        content = ""

        yield {"name": ue_name,
               "id": ue_id,
               "teacher": teachers,
               "year": year,
               "ects": ects,
               "cycle": cycle,
               "faculty": faculty,
               "program": program,
               "campus": campus,
               "url": response.url,
               "content": content}


