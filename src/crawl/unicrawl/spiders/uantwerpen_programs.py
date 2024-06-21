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


""" 
Error is normal for:

- Master in Basisonderwijs - No info
- Archivistiek: erfgoedbeheer en hedendaags documentbeheer - Cooresponds to master in erfgoedstudies
- Master in Politieke wetenschappen - subdivided in other programs that are already crawled
- Master in Chemie = Master in Chemistry
- Master in Biologie - divided into different master of biology
- Master in Bio-ingenieurswetenschappen - divided into other masters already crawled
- Master in de ergotherapeutische wetenschap - KULeuven
- Master-na-master in de literatuurwetenschappen - KULeuven
- Master of Molecular Biology - VUB
- Advanced master of Management - Antwerp Management School
- Advanced master of International Fashion Management - Antwerp Management School
- Advanced master of Innovation and Entrepreneurship - Antwerp Management School
- Advanced master of Global Management - Antwerp Management School
- Advanced master of Global Supply Chain Management - Antwerp Management School
- Advanced master of Human Resources Management - Antwerp Management School
- Advanced master of Finance - Antwerp Management School
- Master of Global Health - Interuniversity program
- Master in de ergotherapeutische wetenschap - Interuniversity program
- Applied Ecohydrology - Interuniversity program
- Master in Open Universiteit - On another website
"""

PROGRAMS_FACULTY = {
    "Faculteit Farmaceutische, Biomedische en Diergeneeskundige Wetenschappen": [
        "Postgraduaat in het klinisch wetenschappelijk onderzoek",
        "Postgraduaat in het ondernemerschap voor wetenschappen en biomedische wetenschappen",
        "Postgraduaat in het milieu en gezondheidswetenschappen",
        "Farmaceutische wetenschappen",
        "Leading International Vaccinology Education",
        "Master in Farmaceutische wetenschappen"
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
        "Psychotherapie",
        "Master of Molecular Biology",
        "Master of Global Health",
        "Master in de ergotherapeutische wetenschap",
        "Musculoskeletale therapie"
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
        "Biologie",
        "Bioscience Engineering: Sustainable Urban Bioscience Engineering",
        "Master of Marine and Lacustrine Science and Management"
    ],
    "Centrum voor Andragogiek": [
        "Postgraduaat in het schoolbeleid"
    ],
    "Centrum Nascholing Onderwijs": [
        "Postgraduaat in de socio-emotionele leerlingbegeleiding in het secundair onderwijs",
        "Postgraduaat in de leerzorg in het secundair onderwijs (Tijdelijk niet aangeboden)",
        "Didactiek Nederlands aan anderstaligen",
        "Postgraduaat in de leerlingenbegeleiding in het secundair onderwijs"
    ],
    "Instituut voor Milieu en Duurzame Ontwikkeling": [
        "Postgraduate of Energy and Climate",
        "Applied Ecohydrology"
    ],
    "Antwerp School of Education": [
        "Postgraduaat in de didactiek Nederlands aan anderstaligen"
    ],
    "Linguapolis": [
        "Postgraduate of Dutch as a Foreign Language in an Academic Context"
    ],
    "Faculteit Letteren en Wijsbegeerte": [
        "Digital Text Analysis",
        "Postgraduate of Asia - Europe Cultural Curatorship Studies",
        "Master-na-master in de literatuurwetenschappen",
        "Digitale tekstanalyse",
        "Master-na-master in de archivistiek: erfgoedbeheer en hedendaags documentbeheer",
        "Research Master of Philosophy",
        "Archivistiek: erfgoedbeheer en hedendaags documentbeheer",
        "Master in Toegepaste taalkunde"
    ],
    "Faculteit Sociale Wetenschappen": [
        "Master in de opleidings- en onderwijswetenschappen",
        "Politieke wetenschappen",
        "Master in gender en diversiteit",
        "Basisonderwijs",
        "Bio-ingenieurswetenschappen"
    ],
    "Faculteit Ontwerpwetenschappen": [
        "Master in Erfgoedstudies"
    ],
    "Antwerp Management School": [  # not crawlable for now (2023) because different website
        "Advanced master of Management",
        "Advanced master of International Fashion Management",
        "Advanced master of Innovation and Entrepreneurship",
        "Advanced master of Human Resources Management",
        "Advanced master of Global Supply Chain Management",
        "Advanced master of Global Management",
        "Advanced master of Finance",
        "Advanced master of China-Europe Business Studies",
        "Centre for Maritime and Air Transport Management"
    ],
    "Centrum Voor Andragogiek": [
        "Postgraduaat schoolleider in het secundair onderwijs"
    ],
    "Open Universiteit": [
        "Open Universiteit"
    ],
    "Faculteit Toegepaste Ingenieurwetenschappen": [
        "Master in Industriële wetenschappen: chemie en biochemie (industrieel ingenieur)",
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

        # didn't find any id for programs so using url
        if 'alle-opleidingen' in response.url:
            program_id = response.url.split("alle-opleidingen/")[1].split("/")[0]
        elif 'all-programmes' in response.url:
            program_id = response.url.split("all-programmes/")[1].split("/")[0]
        else:
            program_id = response.url.split("/")[-2]

        # Check the navigation tab for programme info tabs
        match = False
        # If one of the tab below has been found, call the parse program on it
        for text, url in zip(nav_tabs_text, nav_tabs_urls):
            if text in ["About the programme", "Programme info", "Opleidingsinfo", "Bachelor", "Master",
                        "Over de bachelor", "Over de master", "Tijdens een bachelor", "Opleindingsinfo en FAQ"]:
                match = True
                yield response.follow(url, self.parse_program_info, cb_kwargs={"program_id": program_id})

        if match is False:
            # No programme info available, call the parse program info on the same page
            yield response.follow(response.url, self.parse_program_info, cb_kwargs={"program_id": program_id},
                                  dont_filter=True)

    def parse_program_info(self, response, program_id):

        program_name = response.xpath("//span[@class='main']/text()").get()
        if program_name is None or "(Discontinued)" in program_name or "(Uitdovend)" in program_name:
            return
        program_name = program_name.strip(" ")

        # Determine general info about the program

        # Find cycle and update id and name based on url
        cycle = 'other'
        if "master" in response.url:
            cycle = "master"
            if 'master' not in program_id:
                program_id = 'master-' + program_id
            if not ('master' in program_name or 'Master' in program_name):
                program_name = f"Master in {program_name}"
        elif "bachelor" in response.url:
            cycle = "bac"
            if 'bachelor' not in program_id:
                program_id = 'bachelor-' + program_id
            if not ('bachelor' in program_name or 'Bachelor' in program_name):
                program_name = f"Bachelor in {program_name}"
        elif "manama" in response.url:
            cycle = 'master'
        elif 'pavo' in response.url or 'Postgrad' in program_name:
            cycle = 'postgrad'

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

        # If link is available, continue otherwise check for subprograms
        if link:
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
        else:
            # Some programs have subprograms
            programs_with_subprograms = \
                ["Master in Farmaceutische wetenschappen",
                 "Master in Toegepaste taalkunde",
                 "Master in Industriële wetenschappen: chemie en biochemie (industrieel ingenieur)"]

            if program_name in programs_with_subprograms:
                subprograms_links = response.xpath("//nav[contains(@class, 'navSub')]/ul/li//a/@href").getall()
                for link in subprograms_links:
                    # cur_dict = base_dict.copy()
                    # cur_dict["id"] += " " + link.split("/")[-2]
                    program_id_new = program_id + "-" + link.split("/")[-2]
                    yield response.follow(link, self.parse_program_info, cb_kwargs={"program_id": program_id_new})
                return
            else:
                print(f"Missing link for {program_name}\n{response.url}")
                return

    def parse_study_program(self, response, base_dict):

        # Get courses and ects
        main_tab = f"//section[contains(@id, '-{YEAR}')]"
        # Add text() in a to be sure the course has a name
        courses_links = response.xpath(f"{main_tab}//h5//a[text()]/@href").getall()
        if len(courses_links) == 0:
            # Check if there are no subprograms
            first_path = ("//nav[contains(@class, 'navSub')]//li[a[contains(text(), 'Studieprogramma') "
                          "or contains(text(), 'Study programme')]]//li/a/")
            sub_programs_links = response.xpath(f"{first_path}@href").getall()
            sub_programs_names = response.xpath(f"{first_path}text()").getall()
            second_path = ("//nav[contains(@class, 'navSub') and header[h2[a[contains(text(), 'Studieprogramma') "
                           "or contains(text(), 'Study programme')]]]]//li/a/")
            sub_programs_links += response.xpath(f"{second_path}@href").getall()
            sub_programs_names += response.xpath(f"{second_path}text()").getall()

            if len(sub_programs_links) != 0:
                for name, link in zip(sub_programs_names, sub_programs_links):
                    cur_dict = base_dict.copy()
                    program_id_new = base_dict['id'] + "-" + link.split("/")[-2]
                    cur_dict['id'] = program_id_new
                    program_name_new = base_dict['name'] + ' - ' + name
                    cur_dict['name'] = program_name_new
                    yield response.follow(link,
                                          self.parse_study_program,
                                          cb_kwargs={"base_dict": cur_dict})
                return
            else:
                print(f"No courses for {base_dict['name']}")
                return

        courses_codes = [link.split("-")[1].split("&")[0] for link in courses_links]
        ects = response.xpath(f"{main_tab}//div[@class='spec points']/div[@class='value']/text()").getall()
        if len(ects) == 0:
            ects = response.xpath(f"//div[@class='spec points']/div[@class='value']/text()").getall()
        ects = [int(e.split(" ")[0].replace('\n', '').replace('\t', '')) for e in ects]

        # One course can be several times in the same program
        courses_codes, ects = zip(*list(set(zip(courses_codes, ects))))

        cur_dict = {
            "url": response.url,
            "courses": courses_codes,
            "ects": ects
        }

        yield {**base_dict, **cur_dict}
