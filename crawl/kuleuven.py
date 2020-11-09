# -*- coding: utf-8 -*-

import argparse

from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags

import settings as s

class KuleuvenSpider(scrapy.Spider):
    name = "kuleuven"

    def start_requests(self):
        base_url = s.KULEUVEN_URL
        yield scrapy.Request(url=base_url, callback=self.parse)

    def parse(self, response):
        for href in response.xpath("//div[contains(@class, 'level_4')]//ul//li//a/@href").getall():
            yield response.follow(href, self.parse_formation1)

    def parse_formation1(self, response):
        href = response.xpath('//div[h1[contains(text(), "Programme summary")]]/ul/li/a/@href')
        yield response.follow(href, self.parse_formation2)

    def parse_formation2(self, response):
        for href in [None, None]
        yield response.follow(href, self.parse_course)

    def parse_course(self, response):
        yield None

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

    process.crawl(KuleuvenSpider)
    process.start()  # the script will block here until the crawling is finished
    print('All done.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl the Uantwerp courses catalog.')
    parser.add_argument("--output", default="output.json".format(__file__), type=str, help="Output file")
    parser.add_argument("--year", default="2020", type=str, help="Academic Year")
    args = parser.parse_args()
    main(args.output)
