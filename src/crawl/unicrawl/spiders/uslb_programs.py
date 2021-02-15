# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

from config.settings import YEAR
BASE_URL = "https://www.usaintlouis.be/sl/enseignement_prog2020.html"


class USLBProgramsSpider(scrapy.Spider, ABC):
    name = "uslb-programs"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/uslb_programs_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_offer)

    def parse_offer(self, response):

        # Bachelor programs
        faculties_names = response.xpath("//p[@class='p2']//a[contains(text(), 'Faculté')]/text()").getall()
        bachelor_programs_links = response.xpath("//p[@class='p5']//a/@href").getall()[:-1]
        # A bit hand-made but the website is really badly done
        bachelor_programs_number = [4, 2, 6, 1]
        first_program = 0
        last_program = 0
        for i, fac in enumerate(faculties_names):
            last_program += bachelor_programs_number[i]
            program_links = bachelor_programs_links[first_program:last_program]
            first_program += bachelor_programs_number[i]
            for link in program_links:
                base_dict = {"id": link.split("/")[-1].replace(".html", ''),
                             "name": '',
                             "faculty": fac,
                             "cycle": 'bac',
                             "campus": ''}  # couldn't find any campus information
                yield response.follow(link, self.get_study_programme_link, cb_kwargs={'base_dict': base_dict})

        # Master programs
        master_program_links = response.xpath("//p//a[contains(text(), 'Master')]/@href").getall()
        for link in master_program_links:
            # Some masters are given at uclouvain and unamur
            if 'uclouvain.be' in link or 'unamur' in link:
                continue
            base_dict = {"id": link.split("/")[-1].replace(".html", ''),
                         "name": '',
                         "faculty": '',  # No fac for masters it seems
                         "cycle": 'master',
                         "campus": ''}  # couldn't find any campus information
            yield response.follow(link, self.get_study_programme_link, cb_kwargs={'base_dict': base_dict})

    def get_study_programme_link(self, response, base_dict):

        study_program_link = response.xpath("//a[text()='Programme']/@href").get()
        yield response.follow(study_program_link, self.parse_study_program, cb_kwargs={'base_dict': base_dict})

    def parse_study_program(self, response, base_dict):

        cur_dict = base_dict.copy()

        # There can be subprograms
        subprograms_links = response.xpath("//p[@class='p4']//a/@href").getall()
        if len(subprograms_links) != 0:
            for link in subprograms_links:
                yield response.follow(link, self.parse_study_program, cb_kwargs={'base_dict': base_dict})
            return

        program_name = response.xpath("//p[@class='ProgrammeTitre']/text()").get()
        cur_dict["name"] = program_name
        # Find additional subprogram name
        subprogram_name = response.xpath("//div[@id='honglet1']//p[contains(text(), 'Majeure')][1]/text()").get()
        if subprogram_name is not None:
            cur_dict["id"] += "_" + response.url.split("_")[-1].replace(".html", '')
            subprogram_name = subprogram_name.strip("\r ")
            cur_dict["name"] += f" {subprogram_name}" if subprogram_name is not None else ''

        courses_codes = response.xpath("//div[@id='honglet1']//td[@class='courssigle']/text()").getall()
        if len(courses_codes) == 0:
            courses_codes = response.xpath("//td[@class='courssigle']/text()").getall()
        courses_codes = [code.strip("\r ") for code in courses_codes]
        cur_dict['courses'] = courses_codes

        nb_columns = 3
        ects = response.xpath("//div[@id='honglet1']//td[@class='courscredits3b']/text()").getall()[4:]
        if len(ects) == 0:
            nb_columns = 2
            ects = response.xpath("//div[@id='honglet1']//td[@class='courscredits2b']/text()").getall()[3:]
        if len(ects) == 0:
            nb_columns = 1
            ects = response.xpath("//td[@class='courscredits1b']/text()").getall()[1:]
        ects = [e.strip('\r ') for e in ects]
        ects = [int(e) if e != '' else 0 for e in ects]

        # Merge columns
        ects_merged = []
        if nb_columns > 1:
            for i in range(int(len(ects)/nb_columns)):
                if nb_columns == 3:
                    ects_merged += [max([ects[i*3], ects[i*3+1], ects[i*3+2]])]
                elif nb_columns == 2:
                    ects_merged += [max([ects[i*2], ects[i*2+1]])]
            cur_dict['ects'] = ects_merged
        else:
            cur_dict['ects'] = ects

        yield cur_dict