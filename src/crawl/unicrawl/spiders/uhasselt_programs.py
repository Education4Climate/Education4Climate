from pathlib import Path

import scrapy
from abc import ABC
import bs4

from config.settings import YEAR

BASE_URL = 'https://uhintra03.uhasselt.be/studiegidswww/opleiding.aspx'

BASE_DATA = {
    "__EVENTTARGET": "beschridDDL$ctl00",
    "__EVENTARGUMENT": "",
    "__LASTFOCUS": "",
    "ihTaal": "01",
    "ihBeschrid": "",
    "ihItemid": "",
    "ihVisible": "",
    "beschridAcjaar$ctl00": "2020",
}


class UHasseltProgramSpider(scrapy.Spider, ABC):
    name = 'uhasselt-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../data/crawling-output/uhasselt_programs_{YEAR}.json')
    }

    def start_requests(self):
        yield scrapy.Request(
            url=BASE_URL,
            callback=self.parse_main
        )

    def parse_main(self, response):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        list_progs = [(e['value'], e.text) for e in soup.find_all('select')[1].find_all('option')[1:]]
        print(list_progs)
        program_ids = response.xpath("//select[2]//option/@value").getall()[1:]
        progam_names = response.xpath("//select[2]//option/text()").getall()[1:]
        print(program_ids)

        #BASE_DATA['__VIEWSTATE'] = soup.find(id='__VIEWSTATE')['value']
        BASE_DATA['__VIEWSTATE'] = response.xpath("//input[@id='__VIEWSTATE']/@value").get()
        #BASE_DATA['__VIEWSTATEGENERATOR'] = soup.find(id='__VIEWSTATEGENERATOR')['value']
        BASE_DATA['__VIEWSTATEGENERATOR'] = response.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value").get()

        for prog, prog_name in list_progs:
            cur_data = BASE_DATA.copy()
            cur_data['beschridDDL$ctl00'] = prog

            cycle = ''
            if 'bachelor' in prog_name:
                cycle = 'bac'
            elif 'master' in prog_name:
                cycle = 'master'
            elif 'Postgraduaat' in prog_name:
                cycle = 'post-grad'

            base_dict = {"id": prog,
                         "name": prog_name,
                         "cycle": cycle}

            yield scrapy.http.FormRequest(
                BASE_URL,
                callback=self.parse_program,
                formdata=cur_data,
                cb_kwargs={'base_dict': base_dict}
            )

    @staticmethod
    def parse_program(response, base_dict):

        # For simplicity taking only course in tables under tabs 'Modeltraject' (except 'Modeltraject van ...')
        main_path = "//div[contains(text(), 'Modeltraject') and not(contains(text(), 'Modeltraject van'))]" \
                    "/following::td[1]//table//table//tr"
        courses_list = response.xpath(f"{main_path}/td[1]/a/text()").getall()
        courses_ids = [course.split(" ")[0] for course in courses_list]
        if len(courses_ids) == 0:
            return

        ects = response.xpath(f"{main_path}/td[5]/text()").getall()
        ects = [e for e in ects if e != 'SP']
        # Some programs do not have a regular way of displaying ects... (some times 4th sometimes 5th column)
        if len(ects) != len(courses_ids):
            ects = [0]*len(courses_ids)

        # Remove duplicates
        courses_ids, ects = zip(*list(set(zip(courses_ids, ects))))

        # Didn't find any info on campus or faculty
        cur_dict = {"faculty": '',
                    "campus": '',
                    "courses": courses_ids,
                    "ects": ects}
        yield {**base_dict, **cur_dict}

