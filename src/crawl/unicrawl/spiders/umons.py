# -*- coding: utf-8 -*-

import crawl.config.settings as s
import argparse

import scrapy
from scrapy.crawler import CrawlerProcess

import crawl.config.utils as u


class UmonsSpider(scrapy.Spider):
    name = "umons"

    def start_requests(self):
        base_url = s.UMONS_URL
        yield scrapy.Request(url=base_url, callback=self.parse)

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
        #TODO:
        data = {}
        yield data

def main(output):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': output
    })

    process.crawl(UmonsSpider)
    process.start() # the script will block here until the crawling is finished
    print('All done.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Craw the Umons courses catalog.')
    parser.add_argument("--output", default="output.json", type=str, help="Output file")
    parser.add_argument("--year", default="2020", type=str, help="Year")
    args = parser.parse_args()
    YEAR = str(args.year)
    main(args.output)