from abc import ABC

import scrapy

from config.settings import YEAR
from config.utils import cleanup

BASE_URL = "https://studiegids.ugent.be/{year}/EN/FACULTY/A/{cycle}/{cycle}.html"


class UgentProgramSpider(scrapy.Spider, ABC):
    name = 'ugent-programs'
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/ugent_programs_{YEAR}.json',
    }

    def start_requests(self):
        for deg in ('BACH', 'MABA'):
            yield scrapy.Request(
                url=BASE_URL.format(year=YEAR, cycle=deg),
                callback=self.parse_main
            )

    def parse_main(self, response):
        faculties_links = response.xpath("//li[a[@target='_top']]/a/@href").getall()
        for link in faculties_links:
            yield response.follow(link, self.parse_programmes)

    @staticmethod
    def parse_programmes(response):
        id = cleanup(response.url.split('/')[-2])
        name = cleanup(response.xpath("//h1")[-1].get())
        cycle = cleanup(name.split(' ')[0])
        cur_dict = {'id': id,
                    'name': name,
                    'cycle': cycle}
        yield cur_dict
