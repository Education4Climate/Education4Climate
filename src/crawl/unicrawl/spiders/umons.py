# -*- coding: utf-8 -*-

import argparse

import scrapy
from scrapy.crawler import CrawlerProcess

import config.settings as s
import config.utils as u


class UmonsSpider(scrapy.Spider):
    name = "umons"

    def start_requests(self):
        base_urls = ["https://web.umons.ac.be/fmp/en/loffre-de-formation-2/", 
                    "https://web.umons.ac.be/fau/en/loffre-de-formation/"]
        for url in base_urls:
            yield scrapy.Request(url=url, callback=self.parse_faculty, dont_filter = True)

    def parse(self, response):
        pass

    def parse_faculty(self, response):
        # Leaving out PhDs, formations for adults and other special formations.
        bachelors = response.xpath('//li[a/text()="1st Cycle: Bachelor"]/ul/li/a/@href').getall()
        masters = response.xpath('//li[a/text()="2nd Cycle: Master"]/ul/li/a/@href').getall()
        if not bachelors:
            bachelors_details = response.xpath('//a[text()="1st Cycle: Bachelor"]/@href').get()
            yield response.follow(bachelors_details, self.parse_details)
        else:
            for bachelor in bachelors:
                yield response.follow(bachelor, self.parse_prog)
        if len(masters) == 0:
            masters_details = response.xpath('//a[text()="2nd Cycle: Master"]/@href').get()
            yield response.follow(masters_details, self.parse_details)
        else:
            for master in masters:
                yield response.follow(master, self.parse_prog)
        
    def parse_details(self, response):
        programs = response.xpath('//article[@class="shortcode-training training-small scheme-fmp"]/a/@href').getall()
        for program in programs:
            yield response.follow(program, self.parse_prog)

    def parse_prog(self, response):
        href = response.xpath('//a[contains(@class, "button-primary-alt scheme-background scheme-background-hover")]/@href').get()
        yield response.follow(href, self.parse_prog_detail)  

    def parse_prog_detail(self, response):
        for href in response.css('a.linkue::attr(href)').getall():
            yield response.follow(href, self.parse_course)
        

    @staticmethod
    def parse_course(response):
        print(response)
        first_block = response.css('table.UETbl td::text').getall()

        data = {
            'class':        u.cleanup(response.css("td.UETitle").get()),
            'shortname':    u.cleanup(first_block[0]),
            'year':         u.cleanup(response.css('td.toptile::text').get().split(' ')[2]),
            # 'location':     u.cleanup(response.css("span.location::text").get()),
            'teachers':     u.cleanup(response.css('table.UETbl')[0].css('li::text').get()),
            'language':     u.cleanup(response.css('table.UETbl')[1].css('li::text').get()),
            'prerequisite': u.cleanup(response.xpath('//div[p/text() = "Compétences préalables"]/p[@class="texteRubrique"]').get()),
            # 'theme':        u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Thèmes')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            # 'goal':         u.cleanup(response.xpath("normalize-space(.//div[div[contains(text(),'Acquis')]]/div[@class='col-sm-10 fa_cell_2'])").get()),
            'content':      u.cleanup(response.xpath('//div[p/text() = "Contenu de l\'UE"]/p[@class="texteRubrique"]').get()),
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
