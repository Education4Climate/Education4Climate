# -*- coding: utf-8 -*-

import scrapy
import argparse

import scrapy
from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags


#<div class="champ contenu_formation toolbox">

class ULBSpider(scrapy.Spider):
    name = "ulb"

    def start_requests(self):
        base_url = 'https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes'
        yield scrapy.Request(url=base_url, callback=self.parse)

    def parse(self, response):
        for href in response.css("a[href^='https://www.ulb.be/fr/programme/']::attr(href)"):
            yield response.follow(href, self.parse_course)

    def parse_course(self, response):
        data = {
            'type':         response.xpath("//div//strong[contains(text(), 'Type de titre')]/following::p").get(),
            'duration':     response.xpath("//div//strong[contains(text(), 'de la formation')]/following::p").get(),
            'language':     response.xpath("//div//strong[contains(text(), 'Campus')]/following::p").get(),
            'category':     response.xpath("//div//strong[contains(text(), '(s) et universit')]/following::a[1]").get(),
            'faculty':      response.xpath("//div//strong[contains(text(), '(s) et universit')]/following::a[2]").get(),
            'url':          response.url
        }
        yield data


def main(output):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': output
    })

    process.crawl(ULBSpider)
    process.start() # the script will block here until the crawling is finished
    print('All done.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl the UCL courses catalog.')
    parser.add_argument("--output", default="output.json", type=str, help="Output file")
    args = parser.parse_args()
    main(args.output)