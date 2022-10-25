# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

# Get only 'Academische opleiding'
BASE_URL = "https://www.uantwerpen.be/nl/studeren/aanbod/alle-opleidingen/?s=16&f=124"
# Note: cannot crawl the Antwerp Management School courses (not on the same website)
# Note: it is normal to have 'missing links' messages for Chemie, Biologie, Polieke wetenschappen,
#   Farmaceutische wetenschappen. These are 'overarching' programs which are subdivided into smaller
#   programs which are crawled by the algorithm.

PROGRAMS_FACULTY = {
    "Faculteit Farmaceutische, Biomedische en Diergeneeskundige Wetenschappen": [
        "Postgraduaat in het klinisch wetenschappelijk onderzoek",
        "Postgraduaat in het ondernemerschap voor wetenschappen en biomedische wetenschappen",
        "Postgraduaat in het milieu en gezondheidswetenschappen",
        "Farmaceutische wetenschappen"
    ],
    "Faculteit Geneeskunde en Gezondheidswetenschappen": [
        "Postgraduate of Algology",
        "Postgraduaat in de psychotherapie - jeugd en context: optie 1",
        "Postgraduaat in de psychotherapie - jeugd en context: optie 2",
        "Postgraduaat in de psychotherapie: optie volwassenen",
        "Postgraduaat in de radioprotectie",
        "Postgraduaat in het rampenmanagement",
        "Postgraduaat in de systeemtheoretische psychotherapie",
        "Postgraduaat verpleegkundige in de huisartspraktijk",
        "Psychotherapie"
    ],
    "Faculteit Rechten": [
        "Postgraduaat in het aansprakelijkheidsrecht en het verzekeringsrecht",
        "Postgraduaat in het gezondheidsrecht en gezondheidsethiek",
        "Postgraduaat in de preventieadviseur niveau 1"
    ],
    "Faculteit Wetenschappen": [
        "Postgraduaat in de adviseur gevaarlijke stoffen",
        "Educatieve master",
        "Chemie",
        "Biologie"
    ],
    "Centrum voor Andragogiek": [
        "Postgraduaat in het schoolbeleid"
    ],
    "Centrum Nascholing Onderwijs": [
        "Postgraduaat in de socio-emotionele leerlingbegeleiding in het secundair onderwijs",
        "Postgraduaat in de leerzorg in het secundair onderwijs (Tijdelijk niet aangeboden)",
        "Didactiek Nederlands aan anderstaligen"
    ],
    "Instituut voor Milieu en Duurzame Ontwikkeling": [
        "Postgraduate of Energy and Climate"
    ],
    "Antwerp School of Education": [
        "Postgraduaat in de didactiek Nederlands aan anderstaligen"
    ],
    "Linguapolis": [
        "Postgraduate of Dutch as a Foreign Language in an Academic Context"
    ],
    "Faculteit Letteren en Wijsbegeerte": [
        "Digital Text Analysis",
        "Postgraduate of China-EU Cultural Curatorship Studies"
    ],
    "Faculteit Sociale Wetenschappen": [
        "Master in de opleidings- en onderwijswetenschappen",
        "Politieke wetenschappen"
    ],
    "Faculteit Ontwerpwetenschappen": [
        "Erfgoedstudies"
    ]
}


class UAntwerpenProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for UAntwerpen
    """

    name = "uantwerpen-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}uantwerpen_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(url=BASE_URL, callback=self.parse_main)

    def parse_main(self, response):

        program_links = response.xpath("//section[contains(@class, 'courseItem')]/a/@href").getall()
        for href in program_links:
            yield response.follow(href, self.find_program_info_tab)

    def find_program_info_tab(self, response):

        nav_tabs_text = response.xpath("//nav[contains(@class, 'navSection')]//a/text()").getall()
        nav_tabs_urls = response.xpath("//nav[contains(@class, 'navSection')]//a/@href").getall()

        # Check the navigation tab for programme info tabs
        match = False
        program_id = response.url.split("/")[-2]  # didn't find any id for programs so using url

        # There is a problem of accessibility of the courses page of this program
        if program_id == 'bachelor-geschiedenis-studeren':
            return

        for text, url in zip(nav_tabs_text, nav_tabs_urls):
            if text in ["About the programme", "Programme info", "Opleidingsinfo", "Bachelor", "Master",
                        "Over de bachelor", "Over de master", "Tijdens een bachelor", "Opleindingsinfo en FAQ"]:
                match = True
                yield response.follow(url, self.parse_program_info, cb_kwargs={"program_id": program_id})

        if match is False:
            # No programme info available, call the parse program info on the same page
            yield response.follow(response.url, self.parse_program_info, cb_kwargs={"program_id": program_id})

    def parse_program_info(self, response, program_id):

        program_name = response.xpath("//span[@class='main']/text()").get()
        if program_name is None or "(Discontinued)" in program_name or "(Uitdovend)" in program_name:
            return
        program_name = program_name.strip(" ")

        # Two programs have subprograms: 'Industriële wetenschappen: chemie en biochemie (industrieel ingenieur)' and
        #  'Toegepaste taalkunde'
        programs_with_subprograms = ["Industriële wetenschappen (industrieel ingenieur): chemie en biochemie",
                                     "Toegepaste taalkunde"]
        if program_name in programs_with_subprograms:
            subprograms_links = response.xpath("//nav[contains(@class, 'navSub')]/ul/li/a/@href").getall()
            for link in subprograms_links:
                # cur_dict = base_dict.copy()
                # cur_dict["id"] += " " + link.split("/")[-2]
                program_id_new = program_id + " " + link.split("/")[-2]
                yield response.follow(link, self.parse_program_info, cb_kwargs={"program_id": program_id_new})
            return

        faculties = response.xpath("//div[contains(@class, 'managedContent')]"
                                   "//li/a[contains(text(), 'Facult') or contains(text(), 'Institu')]/text()").getall()
        # Small fix for program manama-fiscaal-recht
        faculties = [f for f in faculties if f != 'procedure van de Faculteit Rechten']
        # For the programs for which the faculty is not specified, we hard-coded it.
        if len(faculties) == 0:
            for faculty, programs_ in PROGRAMS_FACULTY.items():
                if program_name in programs_:
                    faculties = [faculty]
                    break
            # If faculty is still None, throw an error to inform that you have
            # to potentially add this information to the dedicated dictionary
            # Potential 'errors' can occur due to the presentation of master programs on the bachelor page
            # However, this does not constitute a problem as the master program are anyway captured.
            assert len(faculties) != 0, f"Missing faculty for program '{program_name}'"

        # Can have several campuses
        campuses = response.xpath("//div[contains(@class, 'managedContent')]"
                                  "//li/a[contains(text(), 'ampus')]/text()").getall()
        campuses = [campus for campus in campuses if campus is not None]

        # Find the study programme link
        # Search link in the side-panel
        link = response.xpath("//nav[contains(@class, 'navSub')]//li/a[contains(text(), 'Studieprogramma')"
                              " or contains(text(), 'Study programme')]/@href").get()
        if link is None:
            link = response.xpath("//nav[contains(@class, 'navSection')]//a[contains(text(), 'Studieprogramma')"
                                  " or contains(text(), 'Study programme')]/@href").get()
        # If still no link available, display information to check where the problem comes from
        if link is None:
            print(f"Missing link for {program_name}\n{response.url}")
            return

        # Find cycle and update id and name based on url
        cycle = 'other'
        if "master" in link:
            cycle = "master"
            if 'master' not in program_id:
                program_id = 'master-' + program_id
            if not('master' in program_name or 'Master' in program_name):
                program_name = f"Master in {program_name}"
        elif "bachelor" in link:
            cycle = "bac"
            if 'bachelor' not in program_id:
                program_id = 'bachelor-' + program_id
            if not('bachelor' in program_name or 'Bachelor' in program_name):
                program_name = f"Bachelor in {program_name}"
        elif "manama" in link:
            cycle = 'master'
        elif 'pavo' in link or 'Postgrad' in program_name:
            cycle = 'postgrad'

        cur_dict = {
            'id': program_id,
            'name': program_name,
            'cycle': cycle,
            'faculties': faculties,
            'campuses': campuses,
            'url': response.url
        }

        yield response.follow(link,
                              self.parse_study_program,
                              cb_kwargs={"base_dict": cur_dict})

    @staticmethod
    def parse_study_program(response, base_dict):

        # Get courses and ects
        main_tab = f"//section[contains(@id, '-{YEAR}')]"
        courses_links = response.xpath(f"{main_tab}//h5//a/@href").getall()
        if len(courses_links) == 0:
            return
        courses_codes = [link.split("-")[1].split("&")[0] for link in courses_links]
        ects = response.xpath(f"{main_tab}//div[@class='spec points']/div[@class='value']/text()").getall()
        ects = [int(e.split(" ")[0].replace('\n', '').replace('\t', '')) for e in ects]

        # One course can be several times in the same program
        courses_codes, ects = zip(*list(set(zip(courses_codes, ects))))

        cur_dict = {
            "url": response.url,
            "courses": courses_codes,
            "ects": ects
        }

        yield {**base_dict, **cur_dict}
