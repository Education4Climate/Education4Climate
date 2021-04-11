from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://studiegids.ugent.be/{year}/NL/FACULTY/{faculty}/{cycle}/{cycle}.html"


class UGentProgramSpider(scrapy.Spider, ABC):
    name = 'ugent-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ugent_programs_{YEAR}_pre.json')
    }

    def start_requests(self):
        faculties_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K']
        for faculty_code in faculties_codes:
            for deg in ('BACH', 'MABA', 'EDMA'):
                yield scrapy.Request(
                    url=BASE_URL.format(year=YEAR, faculty=faculty_code, cycle=deg),
                    callback=self.parse_main
                )

    def parse_main(self, response):
        program_links = response.xpath("//li[a[@target='_top']]/a/@href").getall()
        program_names = response.xpath("//li[a[@target='_top']]/a/text()").getall()
        for link, program_name in zip(program_links, program_names):
            program_name = program_name.replace("  ", '').replace("\n", '')\
                .replace('-', ' - ').replace('  ', ' ').strip(" ")
            yield response.follow(link, self.parse_programmes, cb_kwargs={'program_name': program_name})

    def parse_programmes(self, response, program_name):
        program_id = response.url.split('/')[-2]
        # program_name = response.xpath("//article//h1/text()").get()
        cycle = 'bac' if 'Bachelor' in program_name else 'master'
        faculty = response.xpath("//div/h2/text()").get()
        # TODO: make faculty a list?
        faculty = faculty.split('\n')[0].strip(" \n")
        version = response.xpath("//div[@class='menuHeader'][contains(text(), 'Program')]/text()").get()
        version = version.split(' ')[-2].strip(")")

        base_dict = {'id': program_id,
                     'name': program_name,
                     'cycle': cycle,
                     'faculty': faculty,
                     'campus': '',  # Didn't find campus information
                     'url': response.url,
                     }

        link = f"{response.url.split('.html')[0]}{version}(0)/{program_id}.html"
        yield response.follow(link, self.parse_course_list, cb_kwargs={"base_dict": base_dict})

    def parse_course_list(self, response, base_dict):

        # Get list of courses in this subprogram
        courses_ids = [url.split('/')[-1].strip('.pdf')
                       for url in response.xpath("//td[@class='cursus']//a/@href").getall()]
        courses_names = []
        courses_ects = []
        courses_teachers = []
        for courses_id in courses_ids:
            course_xpath = f"//td[@class='cursus']//a[contains(@href, '{courses_id}')]"
            courses_names += [response.xpath(f"{course_xpath}/text()").get().strip(" ").replace(' ]', ']')]
            courses_ects += [response.xpath(f"{course_xpath}"
                                            f"/following::td[@class='studiepunten'][1]/text()").get()]
            courses_teachers += [response.xpath(f"{course_xpath}"
                                                f"/following::td[@class='lesgever'][1]//text()").get()]
        courses_ects = [float(e) if '.' in e else int(e) for e in courses_ects]
        courses_teachers = [f"{' '.join(t.split(' ')[1:])} {t.split(' ')[0]}" if t is not None else None
                            for t in courses_teachers]
        print(len(courses_ids), len(courses_names), len(courses_ects), len(courses_teachers))
        if len(courses_ids) != len(courses_names) or len(courses_ids) != len(courses_ects) or len(courses_teachers) != len(courses_ids):
            exit()
        # If there are any, create an entry in the output file
        if len(courses_ids) != 0:
            cur_dict = {'courses': courses_ids,
                        'ects': courses_ects,
                        'courses_names': courses_names,
                        'courses_teachers': courses_teachers}
            yield {**base_dict, **cur_dict}

        # Open subprograms
        subprograms = [content.split("'")[3] for content
                       in response.xpath('//a[@onclick[contains(text(), toggleContent)]]/@onclick').getall()]
        for subprogram in subprograms:
            url = '/'.join(response.url.split("/")[:-1]) + "/" + subprogram
            yield response.follow(url, self.parse_course_list, cb_kwargs={"base_dict": base_dict})
