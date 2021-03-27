from abc import ABC
from typing import List
from pathlib import Path

import scrapy
# import pdfplumber

from config.settings import YEAR
from config.utils import cleanup
import re
import os
import urllib3

BASE_URL = "https://studiegids.ugent.be/{year}/NL/FACULTY/{faculty}/{cycle}/{cycle}.html"


def extract_id_from_url_ugent(url: str) -> str:
    split_url = re.findall(r"[\w']+", url)
    return split_url[split_url.index("pdf") - 1]


def extract_url_from_toggle_content(toggle_content: str) -> str:
    url = toggle_content.split(",")[1].replace("'", "")
    return url


def extract_ects(ects_list: List[str]) -> List[str]:
    if "Crdt" in ects_list:
        ects_list.remove("Crdt")

    if "" in ects_list:
        ects_list.remove("")
    return ects_list


def extract_year(messy_string: str) ->str:
    year = "".join([j for j in messy_string if j.isdigit()])
    year = year[:4] + '-' + year[4:]
    return year


def extract_teacher(teacher_list: List[str]) -> List[str]:
    if "Instructor" in teacher_list:
        teacher_list.remove("Instructor")

    if "" in teacher_list:
        teacher_list.remove("")
    return teacher_list


def read_pdf(pdf_path: str) -> str:
    page_content = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page_nb in range(len(pdf.pages)):
            first_page = pdf.pages[0]
            page_content += first_page.extract_text()
    return page_content


def download_pdf(pdf_url: str) -> str:
    urllib3.disable_warnings()
    filePath = r"file.pdf"
    with urllib3.PoolManager() as http:
        r = http.request('GET', pdf_url)
        with open(filePath, 'wb') as fout:
            fout.write(r.data)
    return filePath


def delete_pdf(pdf_path: str) -> str:
    os.remove(pdf_path)


def extract_content(pdf_url: str) -> str:
    pdf_path = download_pdf(pdf_url)
    content = read_pdf(pdf_path)
    delete_pdf(pdf_path)
    return content


class UGentProgramSpider(scrapy.Spider, ABC):
    name = 'ugent-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../data/crawling-output/ugent_programs_{YEAR}_pre.json')
    }

    def start_requests(self):
        faculties_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K']
        i = 0
        for faculty_code in faculties_codes:
            for deg in ('BACH', 'MABA'):
                yield scrapy.Request(
                    url=BASE_URL.format(year=YEAR, faculty=faculty_code, cycle=deg),
                    callback=self.parse_main
                )
            i += 1
            if i >= 1:
                break

    def parse_main(self, response):
        program_links = response.xpath("//li[a[@target='_top']]/a/@href").getall()
        i = 0
        for link in program_links:
            print(link)
            yield response.follow(link, self.parse_programmes)
            i += 1
            if i >= 1:
                break

    def parse_programmes(self, response):
        program_id = response.url.split('/')[-2]
        program_name = response.xpath("//article//h1/text()").get()
        cycle = 'bac' if 'Bachelor' in program_name else 'master'
        faculty = response.xpath("//div/h2/text()").get()
        # year = extract_year(cleanup(response.xpath("//h3").get()))
        # version = cleanup(get_program_version(
        #     response.xpath("//div[@class='menuHeader'][contains(text(), 'Programme')]").get()))
        version = response.xpath("//div[@class='menuHeader'][contains(text(), 'Program')]/text()").get()
        version = version.split(' ')[-2].strip(")")

        base_dict = {'id': program_id,
                     'name': program_name,
                     'cycle': cycle,
                     'faculty': faculty,
                     'campus': '',  # Didn't find campus information
                     'url': response.url,
                     }
                     # 'year': year,
                     #'version(debug)': version}

        link = f"{response.url.split('.html')[0]}{version}(0)/{program_id}.html"
        print(link)
        yield response.follow(link, self.parse_course_list, cb_kwargs={"base_dict": base_dict})

    def parse_course_list(self, response, base_dict):

        # Get list of courses in this subprogram
        courses_ids = [url.split('/')[-1].strip('.pdf')
                       for url in response.xpath("//td[@class='cursus']//a/@href").getall()]
        courses_ects = [int(e) for e in response.xpath("//tr[contains(@class, 'rowclass')]"
                                                       "//td[@class='studiepunten']/text()").getall()]
        print(courses_ids)
        print(courses_ects)
        # If there are any, create an entry in the output file
        if len(courses_ids) != 0:
            cur_dict = {'courses': courses_ids,
                        'ects': courses_ects}
            yield {**base_dict, **cur_dict}

        # Open subprograms
        subprograms = [content.split("'")[3] for content
                       in response.xpath('//a[@onclick[contains(text(), toggleContent)]]/@onclick').getall()]
        for subprogram in subprograms:
            url = '/'.join(response.url.split("/")[:-1]) + "/" + subprogram
            yield response.follow(url, self.parse_course_list, cb_kwargs={"base_dict": base_dict})

    @staticmethod
    def parse_course_list_final(response, base_dict):
        urls = ["https://studiegids.ugent.be/" + cleanup(res) for res in response.xpath("//td[@class='cursus']/a/@href").getall()]
        courses_id = [extract_id_from_url_ugent(url) for url in urls]
        # courses_content = [extract_content(url) for url in urls]
        courses_ects = extract_ects([cleanup(res) for res in response.xpath("//td[@class='studiepunten']").getall()])
        courses_teacher = extract_teacher([cleanup(res) for res in response.xpath("//td[@class='lesgever']").getall()])
        final_dict = {**base_dict,
                      **{
                          'url(debug)': response.url,
                          'courses': courses_id,
                          'courses_urls': urls,
                          'courses_ects': courses_ects,
                          'courses_teacher': courses_teacher,
                          # 'courses_content': courses_content
                      }}
        yield final_dict
