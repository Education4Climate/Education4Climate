# -*- coding: utf-8 -*-

import argparse

import scrapy
from scrapy.crawler import CrawlerProcess
#from scrapy.linkextractors import LinkExtractor
from w3lib.html import remove_tags

import config.utils as u


#<div class="champ contenu_formation toolbox">

class ULBSpider(scrapy.Spider):
    name = "ulb"

    def start_requests(self):
        base_url = 'https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes'
        yield scrapy.Request(url=base_url, callback=self.parse)

    def parse(self, response):
        print('Je suis dans parse et voici l url :', response.url)
        for href in response.css("a[class='item-title__element_title']::attr(href)"):
            print('href apres: ', href)
            yield response.follow(href, self.parse_before_prog)

    def parse_before_prog(self, response):
        print('yo')
        yield response.follow('#programme', self.parse_prog)

    def parse_prog(self, response):
        print('URL du cours :', response.url)
        print('requete est faite')
        print(len(response.xpath("//div[@class='prg-programme']")))
        print(response.xpath("//div[@class='prg-programme']"))
        #for href in response.xpath("//div[@class='prg-programme']"):
        #    yield response.follow(href, self.parse_course)

    @staticmethod
    def parse_course(self, response):
        data = {
            'type':         u.cleanup(response.xpath("//div//strong[contains(text(), 'Type de titre')]/following::p").get()),
            'duration':     u.cleanup(response.xpath("//div//strong[contains(text(), 'de la formation')]/following::p").get()),
            'language':     u.cleanup(response.xpath("//div//strong[contains(text(), 'Campus')]/following::p").get()),
            'category':     u.cleanup(response.xpath("//div//strong[contains(text(), '(s) et universit')]/following::a[1]").get()),
            'faculty':      u.cleanup(response.xpath("//div//strong[contains(text(), '(s) et universit')]/following::a[2]").get()),
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
    parser.add_argument("--year", default="2020", type=str, help="Academic Year")
    args = parser.parse_args()
    main(args.output)