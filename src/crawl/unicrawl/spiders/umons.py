# -*- coding: utf-8 -*-

import argparse

import scrapy
from scrapy.crawler import CrawlerProcess

import config.settings as s
import config.utils as u


class UmonsSpider(scrapy.Spider):
    name = "umons"

    def start_requests(self):
        base_url = "http://applications.umons.ac.be/web/fr/pde/2020-2021/cursus/AIN1.htm"
        yield scrapy.Request(url=base_url, callback=self.parse_prog_detail)

    def parse(self, response):
        pass

    def parse_formation(self, response):
        pass

    def parse_prog(self, response):
        pass

    def parse_prog_detail(self, response):
        for href in response.css('a.linkue::attr(href)').getall():
            yield response.follow(href, self.parse_course)
        

    @staticmethod
    def parse_course(response):
        first_block = response.css('table.UETbl td::text').getall()

        data = {
            'class':        u.cleanup(response.css("td.UETitle").get()),
            'shortname':    u.cleanup(first_block[0]),
            # 'year':         u.cleanup(response.css("span.anacs::text").get()),
            # 'location':     u.cleanup(response.css("span.location::text").get()),
            'teachers':     u.cleanup(response.css('table.UETbl')[0].css('li::text').getall()),
            'language':     u.cleanup(response.css('table.UETbl')[1].css('li::text').getall()),
            # 'prerequisite': u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Préalables')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            # 'theme':        u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Thèmes')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            # 'goal':         u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Acquis')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            # 'content':      u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Contenu')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            # 'method':       u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Méthodes')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            # 'evaluation':   u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Modes')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            # 'other':        u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Autres')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            # 'resources':    u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Ressources')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            # 'biblio':       u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Bibliographie')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            # 'faculty':      u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Faculté')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'url':          response.url
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
