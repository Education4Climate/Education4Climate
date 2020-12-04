# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

import config.settings as s
import config.utils as u

UANTWERP_URL = "https://www.uantwerpen.be/en/study/education-and-training/"


class UantwerpSpider(scrapy.Spider, ABC):
    name = "uantwerp"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/uantwerp_courses_{s.YEAR}.json',
    }

    def start_requests(self):
        base_url = UANTWERP_URL
        yield scrapy.Request(url=base_url, callback=self.parse_main)

    def parse_main(self, response):
        for href in response.xpath(
                "//span[contains(text(), 'master')]/preceding::h2/a/@href").getall():
            yield response.follow(href + 'study-programme/', self.parse_formation)

    def parse_formation(self, response):
        for href in response.xpath("//a[@class='iframe cboxElement']/@href").getall():
            yield response.follow(href, self.parse_course)

    @staticmethod
    def parse_course(response):
        data_mapper = {
            # Standard fields :
            'name': "//h1",
            'id': "/html/body/form/div[3]/section/section/table/tbody/tr[1]/td[2]/b",
            'teacher': "/html/body/form/div[3]/section/section/table/tbody/tr[11]/td[2]/a",
            'ects': "/html/body/form/div[3]/section/section/table/tbody/tr[6]/td[2]",
            'content': "/html/body/form/div[3]/section/section/div[1]/div[3]/div/p",
            'language': "/html/body/form/div[3]/section/section/table/tbody/tr[9]/td[2]",
            'year': "/html/body/form/div[3]/section/section/table/tbody/tr[3]/td[2]",
            'campus': "",
            'faculty': "/html/body/form/div[3]/section/section/table/tbody/tr[2]/td[2]/b",
            'cycle': "",
            'formation': "",

            # Other non standard fields :
            'learning_outcome': "/html/body/form/div[3]/section/section/div[1]/div[2]/div",
            # ToDo: Confirm that method = Teaching method
            'method': "/html/body/form/div[3]/section/section/div[1]/div[5]/div",
            # ToDo: Confirm that evalutation = Assessment method
            'evaluation': "/html/body/form/div[3]/section/section/div[1]/div[6]/div",
            'contact_hours': "/html/body/form/div[3]/section/section/table/tbody/tr[5]/td[2]",
            'study_load': "/html/body/form/div[3]/section/section/table/tbody/tr[7]/td[2]",
            'contract_restrictions': "/html/body/form/div[3]/section/section/table/tbody/tr[8]/td[2]",
            'prerequisite': "/html/body/form/div[3]/section/section/div[1]/div[1]/div"
        }

        data = {}
        for field in data_mapper:
            xpath_str = data_mapper[field]
            if xpath_str == '':
                continue
            try:
                data[field] = u.cleanup(response.xpath(xpath_str).get())
            except Exception as e:
                raise ValueError(
                    f"Xpath {xpath_str} does not work for field {field}.\n"
                    f"More information on the error : {e}"
                )
        data['url'] = response.url
        yield data

# Suppression du launcher artisanal, il ne faut pas utiliser ce genre de méthode ultra-roots...
# (il n'utilise alors pas le paramétrage du scraper)
# Pour lancer un crawler et le debugger sous Pycharm :
# Run / Edit configurations
# Choisir la configuration à modifier
# Switcher "Script path" par "Module name" et écrire : scrapy.cmdline
# Parameters : runspider unicrawl/spiders/{nom du script.py}
# Working directory : {chemin absolu de votre dossier unicrawl}\src\crawl
