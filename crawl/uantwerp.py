# -*- coding: utf-8 -*-

import scrapy
import argparse

import scrapy
from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags


class UantwerpSpider(scrapy.Spider):
    name = "uantwerp"

    def start_requests(self):
        base_url = 'https://www.uantwerpen.be/en/study/education-and-training/'
        yield scrapy.Request(url=base_url, callback=self.parse)

    def parse(self, response):
        for href in response.xpath("//span[contains(text(), 'master')]/preceding::h2/a/@href").getall():
            yield response.follow(href + 'study-programme/', self.parse_formation)

    def parse_formation(self, response):
        for href in response.xpath("//a[@class='iframe cboxElement']/@href").getall():
            yield response.follow(href, self.parse_course)

    def parse_course(self, response):
        data_mapper = {
            # Standard fields :
            'name': "//h1",
            'shortname': "/html/body/form/div[3]/section/section/table/tbody/tr[1]/td[2]/b",
            'year': "/html/body/form/div[3]/section/section/table/tbody/tr[3]/td[2]",
            'location': "",
            'prerequisite': "/html/body/form/div[3]/section/section/div[1]/div[1]/div",
            'theme':"",
            # ToDo: Confirm that learning outcomes = goals
            'goal': "/html/body/form/div[3]/section/section/div[1]/div[2]/div",
            'content': "/html/body/form/div[3]/section/section/div[1]/div[3]/div/p",
            # ToDo: Confirm that method = Teaching method
            'method': "/html/body/form/div[3]/section/section/div[1]/div[5]/div",
            # ToDo: Confirm that evalutation = Assessment method
            'evaluation': "/html/body/form/div[3]/section/section/div[1]/div[6]/div",
            'other': "",
            'resources':"",

            # Other non standard fields :
            'contact_hours': "/html/body/form/div[3]/section/section/table/tbody/tr[5]/td[2]",
            'credits': "/html/body/form/div[3]/section/section/table/tbody/tr[6]/td[2]",
            'study_load': "/html/body/form/div[3]/section/section/table/tbody/tr[7]/td[2]",
            'contract_restrictions': "/html/body/form/div[3]/section/section/table/tbody/tr[8]/td[2]",
            'language_of_instruction': "/html/body/form/div[3]/section/section/table/tbody/tr[9]/td[2]",
            'lecturer': "/html/body/form/div[3]/section/section/table/tbody/tr[11]/td[2]/a",
            # ToDo: Study domain = faculty ?
            'study_domain': "/html/body/form/div[3]/section/section/table/tbody/tr[2]/td[2]/b"
        }

        data = {}
        for field in data_mapper:
            xpath_str = data_mapper[field]
            if xpath_str is '':
                continue
            try:
                data[field] = self._cleanup(response.xpath(xpath_str).get())
            except Exception as e:
                raise ValueError("Xpath {} does not work for field {}. "
                                 "\n More information on the error : {}".format(xpath_str, field, e))

        yield data

    def _cleanup(self, data):
        if data is None:
            return ""
        elif isinstance(data, list):
            result = list()
            for e in data:
                result.append(self._cleanup(e))
            return result
        else:
            return remove_tags(data).strip()


def main(output):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': output
    })

    process.crawl(UantwerpSpider)
    process.start()  # the script will block here until the crawling is finished
    print('All done.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl the Uantwerp courses catalog.')
    parser.add_argument("--output", default="output.json".format(__file__), type=str, help="Output file")
    parser.add_argument("--year", default="2020", type=str, help="Academic Year")
    args = parser.parse_args()
    main(args.output)