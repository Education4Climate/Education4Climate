# -*- coding: utf-8 -*-

import argparse

import scrapy
from scrapy.crawler import CrawlerProcess

import config.settings as s
import config.utils as u


class UmonsSpider(scrapy.Spider):
    name = "umons"

    def start_requests(self):
        url = "https://web.umons.ac.be/fr/enseignement/loffre-de-formation-de-lumons/"
        yield scrapy.Request(url=url, callback=self.parse_offer)

    def parse_offer(self, response):
        formations = response.xpath('//span//a[not(contains(@href, "png"))]')
        urls = formations.xpath('@href').getall()
        cycles = formations.xpath('text()').getall()
        assert len(urls) == len(cycles)
        for i in range(len(urls)):
            yield response.follow(urls[i], self.parse_prog, cb_kwargs={'cycle':cycles[i]})

    def parse_details(self, response, cycle):
        programs = response.xpath(
            '//article[starts-with(@class,"shortcode-training training-small scheme-")]/a/@href').getall()
        for program in programs:
            yield response.follow(program, self.parse_prog, cb_kwargs={'cycle':cycle})

    def parse_prog(self, response, cycle):
        href = response.xpath(
            '//a[contains(@class, "button-primary-alt scheme-background scheme-background-hover")]/@href').get()
        if not href:
            yield response.follow(response.url, self.parse_details, cb_kwargs={'cycle':cycle})
        else:
            location = response.xpath(
                '//div[div/text()="Lieu"]').css('div.value::text').get()
            ects = response.xpath(
                '//div[div/text()="Crédits ECTS"]').css('div.value::text').get()
            yield response.follow(url=href, callback=self.parse_prog_detail, cb_kwargs={'location': location, 'ects': ects, 'cycle':cycle})

    def parse_prog_detail(self, response, location, ects, cycle):
        faculty = response.css('td.facTitle::text').get()
        for href in response.css('a.linkue::attr(href)').getall():
            yield response.follow(url=href, callback=self.parse_course, cb_kwargs={'location': location, 'faculty': faculty, 'ects': ects, 'cycle':cycle})

    @staticmethod
    def parse_course(response, location, faculty, ects, cycle):
        first_block = response.css('table.UETbl td::text').getall()

        data = {
            'name':         u.cleanup(response.css("td.UETitle").get()),
            'id':           u.cleanup(first_block[0]),
            'cycle':        u.cleanup(cycle),
            'year':         u.cleanup(response.css('td.toptile::text').get().split(' ')[2]),
            'campus':       u.cleanup(location),
            'ects':         u.cleanup(ects),
            'teachers':     u.cleanup(response.css('table.UETbl')[0].css('li::text').get()),
            'language':     u.cleanup(response.css('table.UETbl')[1].css('li::text').get()),
            'prerequisite': u.cleanup(response.xpath('//div[p/text() = "Compétences préalables"]/p[@class="texteRubrique"]').get()),
            'goal':         u.cleanup(response.xpath('//div[p/text() = "Acquis d\'apprentissage UE"]/p[@class="texteRubrique"]').get()),
            'content':      u.cleanup(response.xpath('//div[p/text() = "Contenu de l\'UE"]/p[@class="texteRubrique"]').get()),
            # 'method':       u.cleanup(response.xpath('//div[p/text() = "Mode d\'enseignement"]/p[@class="texteRubrique"]').get()),
            'faculty':      u.cleanup(faculty),
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
