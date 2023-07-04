from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://pedagogique.he2b.be/cursus/"
DESC_URL = f"https://pedagogique.he2b.be/descriptifs/?anac={YEAR}" + "&nav=0&o={}"

# TODO: remove

import urllib3
def download_pdf(pdf_url: str) -> str:

    urllib3.disable_warnings()
    # file_path = r"file.pdf"
    # FIXME: to change
    file_path = f"/home/duboisa1/shifters/Education4Climate/data/pdfs/he2b/{pdf_url.split('=')[-1]}.pdf"
    with urllib3.PoolManager() as http:
        r = http.request('GET', pdf_url)
        with open(file_path, 'wb') as fout:
            fout.write(r.data)
    return file_path

DESC2_URL = f"https://pedagogique.he2b.be/descriptifs/"

# TODO: only works for Pedagogie


class HE2BProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Haute Ecole Bruxelles-Brabant
    """

    name = 'he2b-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}he2b_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_main)

    def parse_main(self, response):

        program_ids = response.xpath("//select[@class='form-control sel_ori']//option/@value").getall()
        program_names = response.xpath("//select[@class='form-control sel_ori']//option/text()").getall()
        for program_id, program_name in zip(program_ids, program_names):
            yield response.follow(
                url=DESC_URL.format(program_id),
                callback=self.parse_program,
                # cb_kwargs={"program_id": program_id, "program_name": program_name}
            )

    def parse_program(self, response):

        pdf_links = response.xpath("//td[@class='ctrls']/a/@href").getall()
        for i, link in enumerate(pdf_links):
            print(i)
            if i % 10 == 0:
                download_pdf(DESC2_URL + link.split("./")[-1])

    @staticmethod
    def parse_courses(response):

        yield {
            'id': "",
            'name': "",
            'cycle': "",
            'faculties': [],
            'campuses': [],
            'url': response.url,
            'courses': [],
            'ects': [],
            'courses_names': [],
            'courses_urls': []
        }
