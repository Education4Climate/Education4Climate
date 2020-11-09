# -*- coding: utf-8 -*-

import argparse

import scrapy
from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags

import settings as s

class UclSpider(scrapy.Spider):
    name = "ucl"

    def start_requests(self):
        base_url = s.
        yield scrapy.Request(url=base_url, callback=self.parse)

    def parse(self, response):
        for href in response.css("a[href^='https://uclouvain.be/fr/catalogue-formations/']::attr(href)").getall():
            yield response.follow(href, self.parse_formation)

    def parse_formation(self, response):
        for href in response.css(f"li a[href^='/prog-{YEAR}']::attr(href)"):
            yield response.follow(href, self.parse_prog)

    def parse_prog(self, response):
        prog = response.url[21:]
        for href in response.css("li a[href^='" + prog + "-']::attr(href)"):
            yield response.follow(href, self.parse_prog_detail)

    def parse_prog_detail(self, response):
        for href in response.css(f"td.composant-ligne1 a[href^='https://uclouvain.be/cours-{YEAR}-']::attr(href)"):
            yield response.follow(href, self.parse_course)

    def parse_course(self, response):
        data = {
            'class':        self._cleanup(response.css("h1.header-school::text").get()),
            'shortname':    self._cleanup(response.css("span.abbreviation::text").get()),
            'year':        self._cleanup(response.css("span.anacs::text").get()),
            'location':     self._cleanup(response.css("span.location::text").get()),
            'teachers':     self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Enseignants')]]/div/a/text())").getall()),
            'language':     self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Langue')]]/div[@class='col-sm-10 fa_cell_2']/text())").get()),
            'prerequisite': self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Préalables')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'theme':        self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Thèmes')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'goal':         self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Acquis')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'content':      self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Contenu')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'method':       self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Méthodes')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'evaluation':   self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Modes')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'other':        self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Autres')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'resources':    self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Ressources')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'biblio':       self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Bibliographie')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'faculty':      self._cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Faculté')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'url':          response.url
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
    parser = argparse.ArgumentParser(description='Craw the UCL courses catalog.')
    parser.add_argument("--output", default="output.json", type=str, help="Output file")
    parser.add_argument("--year", default="2020", type=str, help="Year")
    args = parser.parse_args()
    YEAR = str(args.year)
    main(args.output)