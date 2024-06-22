from abc import ABC
from pathlib import Path

import pandas as pd
import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = f"https://www.helha.be/"

"""
Normal to have an error for
- Radiothérapie - Spécialisation : no course description
- Santé mentale - Spécialisation : no course description
- Gériatrie - Spécialisation : no course description
- Oncologie - Spécialisation : no course description
- Master en sciences infirmières : no course description
- Psychomotricité : no courses listed
- Icarré
- Datacenter
- Bioqualité en alternance - given in Haute Ecole de Vinci
- RFIE - Réforme de la formation initiale des enseignants
- Go Teaching
- Old - Bachelor from previous years
- METIS - interuniversity program
- Master Ingénierie et Action Sociales (MIAS) : no cours description
"""

FACULTY_NAMES = {
    'agronomique': "Agronomique",
    "artsappliques": "Arts Appliquées",
    "economique": "Economique",
    "education": "Education",
    "sante": "Santé",
    "social": "Social",
    "technique": "Sciences et Technologies"
}


class HELHaProgramSpider(scrapy.Spider, ABC):
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

        program_links = response.xpath("//a[text() = 'Formations']/following::section[1]"
                                       "//li[not(ul[@class='children'])]/a/@href").getall()

        for program_link in program_links:

            # Determine the id based on the url at this stage because the urls become more complex after (and no
            # ids defined for programs by Helha)
            program_id = program_link.split("/")[-2]

            # Bad urls for ids
            if program_id == 'mons' or program_id == 'montignies-sur-sambre':
                program_id = f"informatique-{program_id}"
            if program_id == 'charleroi':
                program_id = "informatique-industrielle"
            if program_id == 'tournai':
                program_id = 'technologie-informatique'
            if 'mastersection' in program_id:
                program_id = f"enseignement-{program_id}"
            if program_id in ['mouscron-tournai', 'la-louviere', 'gilly']:
                program_id = f"infirmier-soins-generaux-{program_id}"
            if program_id == 'master':
                program_id = 'master-expertise-comptable-fiscale'
            if program_id.startswith('orientation'):
                program_id = f"gestion-hoteliere-{program_id}"
            if program_id == 'louvain-la-neuve':
                program_id = f"{program_id}-assistante-sociale"

            main_name = response.xpath(f"//a[@href='{program_link}']/text()").get()
            parent_name = response.xpath(f"//a[@href='{program_link}']//ancestor::ul[@class='children'][1]"
                                         f"/ancestor::li[1]/a/text()").get()

            program_name = f"{parent_name} - {main_name}" if parent_name else main_name

            yield response.follow(
                url=program_link,
                callback=self.parse_nav1,
                cb_kwargs={'program_id': program_id, 'program_name': program_name}
            )

    def parse_nav1(self, response, program_id, program_name):
        """
        Get the first link to course programs from side panel (either direct link to the final page, or need a second
        link)
        """

        # Different cases depending on the link to the courses description
        url = response.xpath("//a[contains(text(), 'Programme de') "
                             "or contains(text(), 'Programme du') or contains(text(), 'Nos formations')]/@href").get()

        # Case 1 - For these names of links, we do not access directly the final page
        if url is not None:

            # Except for 'Spécialisation en santé mentale' and 'Master Communication Stratégique'
            if 'sante-mentale-specialisation' in response.url or 'master-communication' in response.url:
                yield response.follow(
                    url=url,
                    callback=self.parse_program,
                    cb_kwargs={'program_id': program_id, 'program_name': program_name}
                )
                return

            yield response.follow(
                url=url,
                callback=self.parse_nav2,
                cb_kwargs={'program_id': program_id, 'program_name': program_name}
            )
            return

        # Case 2 - For these names of links we arrive directly at the final page
        url = response.xpath("//a[contains(text(), 'Contenu de') or contains(text(), 'Contenus de')]/@href").get()
        if url is not None:
            yield response.follow(
                url=url,
                callback=self.parse_program,
                cb_kwargs={'program_id': program_id, 'program_name': program_name}
            )
            return
        else:
            print(f"No correct link to courses description found for {response.url}")

    def parse_nav2(self, response, program_id, program_name):
        """
        This parser selects the second level of navigation link to the list of courses
        """

        # Special case Master en enseignement
        if 'education/mastersection3' in response.url:
            return

        # Special case with Ingénieur industriel
        if "ingenieur-industriel" in response.url:
            program_links = response.xpath("//li[a[contains(text(), 'Programme de')]]/ul//li/a/@href").getall()
            for url in program_links:
                yield response.follow(
                    url=url,
                    callback=self.parse_program,
                    cb_kwargs={'program_id': program_id, 'program_name': program_name}
                )
            return

        # Special case with Professeur dans le secondaire
        if "regent" in response.url:
            program_links = response.xpath("//li[a[contains(text(), 'Nos formations')]]"
                                           "/ul//li/a[contains(text(), 'AESI')]/@href").getall()
            for url in program_links:
                yield response.follow(
                    url=url,
                    callback=self.parse_program,
                    cb_kwargs={'program_id': program_id, 'program_name': program_name}
                )
            return

        # Other cases
        url = response.xpath("//a[contains(text(), 'Contenu de') or contains(text(), 'Contenus de')"
                             " or contains(text(), 'contenu de')]/@href").get()
        if 'agro-adsa' in response.url:
            url = response.xpath("//a[contains(text(), 'Grille Horaire')]/@href").get()

        yield response.follow(
            url=url,
            callback=self.parse_program,
            cb_kwargs={'program_id': program_id, 'program_name': program_name}
        )

    @staticmethod
    def parse_program(response, program_id, program_name):

        # Special case for 'Ingénieur Industriel'
        if 'ingenieur-industriel' in response.url:
            program_id = response.url.split("/")[-2]
            program_name = response.xpath("//h1//small/text()").get()

        cycle = 'master' if 'master' in program_name.lower() else 'bac'

        faculty = response.xpath("//ul[contains(@class, 'menu-etudes')]/@class").get().split(" ")[-1]

        # Lines containing a pdf link
        # lines_txt = "//tr[contains(@class, 'ue') and td[5]/a]"
        lines_txt = "//tr[td[5]/a]"
        # if 'master-communication' in response.url:
        #     lines_txt = "//tr[td[5]/a]"

        ue_ids = response.xpath(f"{lines_txt}/td[2]//span/text()").getall()
        if len(ue_ids) == 0:
            print(f"No courses for {response.url}")
            return
        campus = response.xpath("//span[@itemprop='addressLocality']/a/text()").get()
        campuses = [campus.replace(" - Campus", '')] if campus else []
        ects = response.xpath(f"{lines_txt}/td[4]//text()").getall()
        ects = [int(float(e)) for e in ects]
        ue_names = response.xpath(f"{lines_txt}/td[1]//text()").getall()
        ue_names = [name.strip("\t\n") for name in ue_names]
        ue_urls = response.xpath(f"{lines_txt}/td[5]/a/@href").getall()
        ue_urls = [url.replace("https://www.helha.be/ects/", '') for url in ue_urls]

        if len(ects) != len(ue_ids) or len(ue_urls) != len(ue_ids) or len(ue_names) != len(ue_ids):
            print(response.url)
            print(len(ue_ids), len(ects), len(ue_names), len(ue_urls))

        yield {
            'id': program_id,
            'name': program_name,
            'cycle': cycle,
            'faculties': [faculty],
            'campuses': campuses,
            'url': response.url,
            'courses': ue_ids,
            'ects': ects,
            'courses_names': ue_names,
            'courses_urls': ue_urls
        }
