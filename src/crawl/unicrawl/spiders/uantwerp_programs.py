# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from config.settings import YEAR

# Get only 'Academische opleiding'
BASE_URL = "https://www.uantwerpen.be/nl/studeren/aanbod/alle-opleidingen/?s=16&f=124"
# Note: cannot crawl the Antwerp Management School courses (not on the same website)


class UantwerpProgramSpider(scrapy.Spider, ABC):
    name = "uantwerp-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../data/crawling-output/uantwerp_programs_{YEAR}.json')
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_main)

    def parse_main(self, response):
        program_links = response.xpath("//section[contains(@class, 'courseItem')]/a/@href").getall()
        for href in program_links:
            yield response.follow(href, self.find_program_info_tab)

    def find_program_info_tab(self, response):

        nav_tabs_text = response.xpath("//nav[contains(@class, 'navSection')]//a/text()").getall()
        nav_tabs_urls = response.xpath("//nav[contains(@class, 'navSection')]//a/@href").getall()

        match = False
        base_dict = {"id": response.url.split("/")[-2]}  # didn't find any id for programs so using url}
        # Check the navigation tab for programme info tabs
        for text, url in zip(nav_tabs_text, nav_tabs_urls):
            if text in ["About the programme", "Programme info", "Opleidingsinfo", "Bachelor", "Master",
                        "Over de bachelor", "Over de master", "Tijdens een bachelor"]:
                yield response.follow(url, self.parse_program_info, cb_kwargs={"base_dict": base_dict})

        if match is False:
            # No programme info available, call the parse program info on the same page
            yield response.follow(response.url, self.parse_program_info, cb_kwargs={"base_dict": base_dict})

    def parse_program_info(self, response, base_dict):

        name = response.xpath("//span[@class='main']/text()").get()
        if name is None or "(Discontinued)" in name:
            return

        # Two programs have subprograms: 'Industriële wetenschappen: chemie en biochemie (industrieel ingenieur)' and
        #  'Toegepaste taalkunde'
        programs_with_subprograms = ["Industriële wetenschappen: chemie en biochemie (industrieel ingenieur)",
                                     "Toegepaste taalkunde"]
        if name in programs_with_subprograms:
            subprograms_links = response.xpath("//nav[contains(@class, 'navSub')]/ul/li/a/@href").getall()
            for link in subprograms_links:
                cur_dict = base_dict.copy()
                cur_dict["id"] += " " + link.split("/")[-2]
                yield response.follow(link, self.parse_program_info, cb_kwargs={"base_dict": cur_dict})
            return

        faculty = response.xpath("//div[contains(@class, 'managedContent')]"
                                 "//li/a[contains(text(), 'Facult') or contains(text(), 'Institu')]/text()").get()
        faculty = "" if faculty is None else faculty
        if faculty is "":
            print(name)
            print(response.url)
        # TODO: can actually have multiple campus, get all and put in a list? need to change all other crawlers?
        campus = response.xpath("//div[contains(@class, 'managedContent')]"
                                "//li/a[contains(text(), 'ampus')]/text()").get()
        campus = "" if campus is None else campus

        cur_dict = {'name': name,
                    'faculty': faculty,
                    'campus': campus,
                    'url': response.url}

        # Find the study programme link
        # Search link in the side-panel
        link = response.xpath("//nav[contains(@class, 'navSub')]//li/a[contains(text(), 'Studieprogramma')"
                              " or contains(text(), 'Study programme')]/@href").get()
        if link is None:
            link = response.xpath("//nav[contains(@class, 'navSection')]//a[contains(text(), 'Studieprogramma')"
                                  " or contains(text(), 'Study programme')]/@href").get()
        if link is None:
            print("Missing link")
            print(name)
            print(response.url)
            return

        yield response.follow(link,
                              self.parse_study_program,
                              cb_kwargs={"base_dict": {**base_dict, **cur_dict}})

    def parse_study_program(self, response, base_dict):

        # Check if there are sub-programs. If so, click on the link and call the function recursively.
        if 0:
            subprograms_links = response.xpath("//nav[@class='navSub']//li/a/@href").getall()
            if len(subprograms_links) != 0:
                for link in subprograms_links:
                    cur_dict = base_dict.copy()
                    cur_dict["id"] += " " + link.split("/")[-2]
                    yield response.follow(link, self.parse_study_program, cb_kwargs={"base_dict": cur_dict})
                return

        # Find cycle based on url
        base_dict["cycle"] = ""
        if "bachelor" in response.url:
            base_dict["cycle"] = "bac"
            base_dict["id"] += '-bac'
            base_dict["name"] = f"Bachelor in {base_dict['name']}"
        elif "master" in response.url:
            base_dict["cycle"] = "master"
            base_dict["id"] += '-master'
            base_dict["name"] = f"Master in {base_dict['name']}"

        # Get courses and ects
        main_tab = f"//section[contains(@id, '-{YEAR}')]"
        courses_links = response.xpath(f"{main_tab}//h5//a/@href").getall()
        if len(courses_links) == 0:
            return
        courses_codes = [link.split("-")[1].split("&")[0] for link in courses_links]
        ects = response.xpath(f"{main_tab}//div[@class='spec points']/div[@class='value']/text()").getall()
        ects = [e.split(" ")[0].replace('\n', '').replace('\t', '') for e in ects]

        # One course can be several times in the same program
        courses_codes, ects = zip(*list(set(zip(courses_codes, ects))))

        cur_dict = {"url": response.url,
                    "courses": courses_codes,
                    "ects": ects}

        yield {**base_dict, **cur_dict}
