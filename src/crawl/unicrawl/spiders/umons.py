# -*- coding: utf-8 -*-

import argparse

import scrapy
from scrapy.crawler import CrawlerProcess

import config.settings as s
import config.utils as u


class UmonsSpider(scrapy.Spider):
    name = "umons"

    def start_requests(self):
        base_urls = [
            "https://web.umons.ac.be/fti-eii/fr/loffre-de-formations/",
            "https://web.umons.ac.be/fweg/fr/offre-de-formation/",
            "https://web.umons.ac.be/fau/fr/loffre-de-formation/",
            "https://web.umons.ac.be/fmp/fr/loffre-de-formation/"
            "https://web.umons.ac.be/fpms/fr/offre-de-formation/",
            "https://web.umons.ac.be/fpse/fr/offre-de-formation/", 
            "https://web.umons.ac.be/eshs/fr/offre-de-formations/"
        ]
        # base_urls =
        for url in base_urls:
            yield scrapy.Request(url=url, callback=self.parse_faculty, dont_filter=True)

        # Only 1 program in the faculty of law
        # Faculty of science website does not link its programs.
        # Had to get them from a search form from the university page.
        program_urls = [
            "https://web.umons.ac.be/droit/fr/training-offer/ba-bdroit/",
            "https://web.umons.ac.be/fs/fr/training-offer/ba-scbioc-c/",
            "https://web.umons.ac.be/fs/fr/training-offer/ba-scbiol/",
            "https://web.umons.ac.be/fs/fr/training-offer/ba-scchim/",
            "https://web.umons.ac.be/fs/fr/training-offer/ba-scinfo/",
            "https://web.umons.ac.be/fs/fr/training-offer/m1-biol60/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-bioefd/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-bioefs/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-bioefa/", #do that
            "https://web.umons.ac.be/fs/fr/training-offer/m2-chimfs/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-chimfd/",
            "https://web.umons.ac.be/fs/fr/training-offer/m1-chim60/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-chimfa/",
            "https://web.umons.ac.be/fs/fr/training-offer/m1-info60-c/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-inffsa/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-infofs/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-infofa/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-infosp-c/",
            "https://web.umons.ac.be/fs/fr/training-offer/m1-info60/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-mathfa/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-matfsf/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-matfsi/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-mathfd/",
            'https://web.umons.ac.be/fs/fr/training-offer/m1-math60/',
            "https://web.umons.ac.be/fs/fr/training-offer/m2-physfd/",
            "https://web.umons.ac.be/fs/fr/training-offer/m1-phys60/",
            "https://web.umons.ac.be/fs/fr/training-offer/ba-scmath/",
            "https://web.umons.ac.be/fs/fr/training-offer/ba-scphys/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-bbmcfd/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-bbmcfs/",
            "https://web.umons.ac.be/fs/fr/training-offer/m2-bbmcfa/"
        ]
        for url in program_urls:
            yield scrapy.Request(url=url, callback=self.parse_prog)

    def parse_faculty(self, response):
        # bachelor_string_1 = "First cycle : Bachelor’s degree"
        bachelor_string = "1er Cycle : Bachelier"
        bachelor_string_bis = "1er cycle : Bachelier"
        masters_string = "2ème Cycle : Master"
        masters_string_bis = "2ème cycle : Master"

        # Leaving out PhDs, formations for adults and other special formations.
        bachelors = response.xpath(
            f'//li[a/text()="{bachelor_string}"]/ul/li/a/@href').getall()
        if not bachelors:
            bachelors = response.xpath(
                f'//li[a/text()="{bachelor_string_bis}"]/ul/li/a/@href').getall()

        masters = response.xpath(
            f'//li[a/text()="{masters_string}"]/ul/li/a/@href').getall()
        if not masters:
            masters = response.xpath(
                f'//li[a/text()="{masters_string_bis}"]/ul/li/a/@href').getall()

        if not bachelors:
            bachelors_details = response.xpath(
                f'//a[text()="{bachelor_string}"]/@href').get()
            if not bachelors_details:
                bachelors_details = response.xpath(
                    f'//a[text()="{bachelor_string_bis}"]/@href').get()
            yield response.follow(bachelors_details, self.parse_details)
        else:
            for bachelor in bachelors:
                yield response.follow(bachelor, self.parse_prog)

        if not masters:
            masters_details = response.xpath(
                f'//a[text()="{masters_string}"]/@href').get()
            if not masters_details:
                masters_details = response.xpath(
                    f'//a[text()="{masters_string_bis}"]/@href').get()
            yield response.follow(masters_details, self.parse_details)
        else:
            for master in masters:
                yield response.follow(master, self.parse_prog)

    def parse_details(self, response):
        programs = response.xpath(
            '//article[starts-with(@class,"shortcode-training training-small scheme-")]/a/@href').getall()
        for program in programs:
            yield response.follow(program, self.parse_prog)

    def parse_prog(self, response):
        href = response.xpath(
            '//a[contains(@class, "button-primary-alt scheme-background scheme-background-hover")]/@href').get()
        if not href:
            yield response.follow(response.url, self.parse_details)
        else:
            location = response.xpath(
                '//div[div/text()="Lieu"]').css('div.value::text').get()
            yield response.follow(url=href, callback=self.parse_prog_detail, cb_kwargs={'location': location})

    def parse_prog_detail(self, response, location):
        faculty = response.css('td.facTitle::text').get()
        for href in response.css('a.linkue::attr(href)').getall():
            yield response.follow(url=href, callback=self.parse_course, cb_kwargs={'location': location, 'faculty': faculty})

    @staticmethod
    def parse_course(response, location, faculty):
        first_block = response.css('table.UETbl td::text').getall()

        data = {
            'class':        u.cleanup(response.css("td.UETitle").get()),
            'shortname':    u.cleanup(first_block[0]),
            'year':         u.cleanup(response.css('td.toptile::text').get().split(' ')[2]),
            'location':     u.cleanup(location),
            'teachers':     u.cleanup(response.css('table.UETbl')[0].css('li::text').get()),
            'language':     u.cleanup(response.css('table.UETbl')[1].css('li::text').get()),
            'prerequisite': u.cleanup(response.xpath('//div[p/text() = "Compétences préalables"]/p[@class="texteRubrique"]').get()),
            'goal':         u.cleanup(response.xpath('//div[p/text() = "Acquis d\'apprentissage UE"]/p[@class="texteRubrique"]').get()),
            'content':      u.cleanup(response.xpath('//div[p/text() = "Contenu de l\'UE"]/p[@class="texteRubrique"]').get()),
            'method':       u.cleanup(response.xpath('//div[p/text() = "Mode d\'enseignement"]/p[@class="texteRubrique"]').get()),
            # 'evaluation':   TODO:,
            # 'resources':    u.cleanup(response.xpath('//tbody[tr/th/text()="Autres références conseillées"]').get()),
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
