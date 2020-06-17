# -*- coding: utf-8 -*-

import scrapy
import argparse

import scrapy
from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags


class UclSpider(scrapy.Spider):
    name = "ucl"

    def start_requests(self):
        base_url = 'https://www.uantwerpen.be/en/study/education-and-training/'
        yield scrapy.Request(url=base_url, callback=self.parse)

    def parse(self, response):
        for href in response.xpath("//span[contains(text(), 'Master')]/preceding::h2/a/@href").getall():
            yield response.follow(href + 'study-programme/', self.parse_formation)

    def parse_formation(self, response):
        for href in response.xpath("//a[@class='iframe cboxElement']/@href").getall():
            yield response.follow(href, self.parse_course)

    def parse_course(self, response):
        data = {
            'name': self._cleanup(response.xpath("//h1").get()),

        }
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

    process.crawl(UclSpider)
    process.start() # the script will block here until the crawling is finished
    print('All done.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl the Uantwerp courses catalog.')
    parser.add_argument("--output", default="output.json", type=str, help="Output file")
    args = parser.parse_args()
    main(args.output)