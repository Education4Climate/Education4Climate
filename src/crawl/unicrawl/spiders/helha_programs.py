from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = f"https://www.helha.be/"


class HEHProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Haute Ecole Louvain en Hainaut
    """

    name = 'helha-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}helha_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_programs)

    def parse_programs(self, response):

        # FIXME: problem with number of programs
        program_links = response.xpath("//a[text() = 'Formations']/following::section[1]//li/a/@href").getall()
        for program_link in program_links:
            print(program_link)
            yield response.follow(
                url=program_link,
                callback=self.parse_sub1
            )

    def parse_sub1(self, response):

        # Case 1
        url = response.xpath("//a[contains(text(), 'Programme de') "
                             "or contains(text(), 'Programme du') or contains(text(), 'Nos formations')]/@href").get()
        if url is not None:

            # Case Spécialisation en santé mentale et Systèmes alimentaires durables et locaux
            if 'sante-mentale-specialisation' in response.url or 'agro-adsa' in response.url:
                yield response.follow(
                    url=url,
                    callback=self.parse_program
                )
                return

            yield response.follow(
                url=url,
                callback=self.parse_sub2
            )
            return

        # Case 2
        url = response.xpath("//a[contains(text(), 'Contenu de') or contains(text(), 'Contenus de')]/@href").get()
        if url is not None:
            yield response.follow(
                url=url,
                callback=self.parse_program
            )
            return

    def parse_sub2(self, response):

        # Special case Master en enseignement
        if 'education/mastersection3' in response.url:
            return

        # Special case with Ingénieur industriel
        if "ingenieur-industriel" in response.url:
            program_links = response.xpath("//li[a[contains(text(), 'Programme de')]]/ul//li/a/@href").getall()
            for url in program_links:
                yield response.follow(
                    url=url,
                    callback=self.parse_program
                )
            return

        # Special case with Professeur dans le secondaire
        if "regent" in response.url:
            program_links = response.xpath("//li[a[contains(text(), 'Nos formations')]]"
                                           "/ul//li/a[contains(text(), 'AESI')]/@href").getall()
            for url in program_links:
                yield response.follow(
                    url=url,
                    callback=self.parse_program
                )
            return

        # Other cases
        url = response.xpath("//a[contains(text(), 'Contenu de') or contains(text(), 'Contenus de')"
                             " or contains(text(), 'contenu de')]/@href").get()
        yield response.follow(
            url=url,
            callback=self.parse_program
        )

    @staticmethod
    def parse_program(response):

        program_id = response.url.split("/")[-2]  # FIXME: to change
        program_name = response.xpath("//span[@class='titlesubtitle']/text()[1]").get()  # FIXME: to change
        program_name = program_name.strip('\n\t')
        cycle = 'bac'  # FIXME: to change
        faculty = 'test'  # FIXME: to change

        # Lines containing a pdf link
        lines_txt = "//tr[contains(@class, 'ue') and td[5]/a]"

        ue_ids = response.xpath(f"{lines_txt}//span/text()").getall()
        if len(ue_ids) == 0:
            print(response.url, ue_ids)
            return
        campus = response.xpath("//span[@itemprop='addressLocality']/a/text()").get()
        ects = response.xpath(f"{lines_txt}//td[4]/text()").getall()
        ects = [int(float(e)) for e in ects]
        ue_names = response.xpath(f"{lines_txt}//td[1]/text()").getall()
        ue_names = [name.strip("\t\n") for name in ue_names]
        ue_urls = response.xpath(f"{lines_txt}//td[5]/a/@href").getall()

        if len(ects) != len(ue_ids) or len(ue_urls) != len(ue_ids) or len(ue_names) != len(ue_ids):
            print(response.url)
            print(len(ue_ids), len(ects), len(ue_names), len(ue_urls))

        yield {
            'id': program_id,
            'name': program_name,
            'cycle': cycle,
            'faculties': [faculty],
            'campuses': [campus],
            'url': response.url,
            'courses': ue_ids,
            'ects': ects,
            'courses_names': ue_names,
            'courses_urls': ue_urls
        }
