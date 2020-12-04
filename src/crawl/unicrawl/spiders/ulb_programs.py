import json
import urllib.parse
from abc import ABC

import bs4
import scrapy

from config.settings import YEAR

BASE_URL = "https://www.ulb.be/servlet/search?" \
           "l=0&beanKey=beanKeyRechercheFormation&&types=formation" \
           "&typeFo={}&s=FACULTE_ASC&limit=999&page=1"

PATH_PROG_URL = urllib.parse.quote('/ws/ksup/programme?anet={}&lang=fr&', safe='{}')
PROG_URL = f'https://www.ulb.be/api/formation?path={PATH_PROG_URL}'


class ULBSpider(scrapy.Spider, ABC):
    name = 'ulb-programs'
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/ulb_programs_{YEAR}.json',
    }

    def start_requests(self):
        for deg in ('BA', 'MA'):
            yield scrapy.Request(
                url=BASE_URL.format(deg),
                callback=self.parse_main
            )

    def parse_main(self, response):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        for p in soup.find_all('div', class_='search-result__result-item'):
            res = {
                "name": p.find('strong').text,
                "url": p.find(class_="item-title__element_title")["href"],
                "faculty": p.find('span', class_='search-result__structure-rattachement').text,
                "code": p.find(class_='search-result__mnemonique').text,
                "location": p.find(class_='search-result-formation__separator').text
            }

            param = res['url'].split('/')[-1].upper()

            yield scrapy.Request(
                url=PROG_URL.format(param),
                callback=self.parse_programme,
                cb_kwargs={'cur_dict': res}
            )

    @staticmethod
    def parse_programme(response, cur_dict):

        json_obj = json.loads(json.loads(response.text)['json'])

        list_cours = []
        for bloc in json_obj['blocs']:
            if bloc['anac'] == YEAR:
                list_cours += bloc['progCourses']

        cur_dict['courses'] = sorted(set(e['id'] for e in list_cours))

        yield cur_dict
