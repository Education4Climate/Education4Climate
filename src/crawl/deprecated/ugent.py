# -*- coding: utf-8 -*-

import scrapy
import argparse

import scrapy
from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags


class UantwerpSpider(scrapy.Spider):
    name = "ugent"

    def start_requests(self):
        base_url = 'https://studiegids.ugent.be/2020/EN/FACULTY/faculteiten.html'
        yield scrapy.Request(url=base_url, callback=self.parse)

    def parse(self, response):
        base_url = '/'.join(response.url.split('/')[:-1])
        for href in  response.xpath("//aside//li[a[@target='_top']]//@href").getall():
            yield {'href': base_url+'/'+href}



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