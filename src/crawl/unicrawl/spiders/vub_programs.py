from abc import ABC

import scrapy

from config.settings import YEAR

BASE_URL = 'https://www.vub.be/opleiding/{}'


class VUBSpider(scrapy.Spider, ABC):
    name = "vub"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/vub_programs_{YEAR}.json',
    }

    def start_requests(self):
        for cycle in ["bachelors", "masters"]:
            yield scrapy.Request(url=BASE_URL.format(cycle), callback=self.parse_main)

    def parse_main(self, response):

        program_links = response.xpath("//div[contains(@class, 'pg-tab')][2]//li//a/@href").getall()
        for link in program_links:
            yield response.follow(link, self.parse_second)

    def parse_second(self, response):
        # TODO: not possible to be crawled? see https://caliweb.vub.be/robots.txt
        #  -> need to change the parameter ROBOTS_OBEY in the crawler settings.py
        # TODO: but if it's possible it's even faster to go directly through there https://caliweb.vub.be/
        plan_link = response.xpath("//ul[@class='rd-opleidingen'][1]//li[1]/a/@href").get()
        yield response.follow(plan_link, self.parse_program)

    @staticmethod
    def parse_program(response):
        yield {"url": response.url}

        if 0:
            title1 = response.xpath("//div[@class='rd-inner-slide']/h3/text()")[0].extract().strip()
            title2 = response.xpath("//div[@class='rd-inner-slide']/h1/text()")[0].extract().strip()

            # TODO : Récupérer la data-key depuis le menu
            content_bloc = response.xpath(
                "//div[@data-key='tab_36996']/section[contains(@class, 'pg-text')]//p/text()")
            content = [c.extract() for c in content_bloc]

            data = {
                'name': f'{title1} {title2}'.title(),
                'id': response.url.rsplit('/', 1)[-1],
                'content': '\n'.join(content)
            }

            yield data
