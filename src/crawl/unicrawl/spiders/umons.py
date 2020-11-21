# -*- coding: utf-8 -*-

import argparse

import scrapy
from scrapy.crawler import CrawlerProcess

import config.settings as s
import config.utils as u


class UmonsSpider(scrapy.Spider):
    name = "umons"

    def start_requests(self):
        base_url = "http://applications.umons.ac.be/web/fr/pde/2020-2021/ue/US-A1-SCINFO-001-M.htm"
        yield scrapy.Request(url=base_url, callback=self.parse_course)

    def parse(self, response):
        pass

    def parse_formation(self, response):
        pass

    def parse_prog(self, response):
        pass

    def parse_prog_detail(self, response):
        pass

    @staticmethod
    def parse_course(response):
        data = {
            'class':        u.cleanup(response.css("td.UETitle").get())
        }
        yield data


def main(output):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': output
    })

    process.crawl(UmonsSpider)
    process.start()  # the script will block here until the crawling is finished
    print('All done.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Craw the Umons courses catalog.')
    parser.add_argument("--output", default="output.json",
                        type=str, help="Output file")
    parser.add_argument("--year", default="2020", type=str, help="Year")
    args = parser.parse_args()
    YEAR = str(args.year)
    main(args.output)
