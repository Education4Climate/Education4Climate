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
        'FEED_URI': f'../../data/crawling-output/uhasselt_programs_{YEAR}.json',
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

        # TODO: Get additional stuff -> need to be more specifig
        main_path = "//div[contains(text(), 'Modeltraject')]/following::td[1]" \
                    "//a[contains(@href, 'opleidings') and contains(@href, 'i=')]"
        courses_list = response.xpath(f"{main_path}/text()").getall()
        courses_list += response.xpath(f"{main_path}/u/text()").getall()
        courses_ids = [course.split(" ")[0] for course in courses_list]
        if len(courses_ids) == 0:
            return

        # TODO: get credits

        # TODO: get faculty and campus --> probably none

        cur_dict = {"courses": courses_ids}
        yield {**base_dict, **cur_dict}

