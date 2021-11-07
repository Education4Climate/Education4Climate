from pathlib import Path

import scrapy
from abc import ABC
import bs4

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = 'https://uhintra03.uhasselt.be/studiegidswww/opleiding.aspx'

BASE_DATA = {
    "__EVENTTARGET": "beschridDDL$ctl00",
    "__EVENTARGUMENT": "",
    "__LASTFOCUS": "",
    "ihTaal": "01",
    "ihBeschrid": "",
    "ihItemid": "",
    "ihVisible": "",
    "beschridAcjaar$ctl00": f"{YEAR}",
}

# This is not great but it's the only way we found to get faculties
FACULTIES_PROGRAMS = {
    "Faculteit Architectuur en Kunst": [
        "bachelor in de interieurarchitectuur", "master in de interieurarchitectuur",
        "Master of Interior Architecture", "bachelor in de architectuur",
        "master in de architectuur", "Educatieve master in de ontwerpwetenschappen"
    ],
    "Faculteit Bedrijfseconomische Wetenschappen": [
        "bachelor handelsingenieur",
        "bachelor in de toegepaste economische wetenschappen",
        "master in de toegepaste economische wetenschappen",
        "Master of Management",
        "bachelor in de handelswetenschappen",
        "master in de handelswetenschappen",
        "master handelsingenieur",
        "Educatieve master in de economie",
        "bachelor handelsingenieur in de beleidsinformatica",
        "master handelsingenieur in de beleidsinformatica"
    ],
    "Faculteit Geneeskunde en Levenswetenschappen": [
        "bachelor in de biomedische wetenschappen",
        "Master of Biomedical Sciences",
        "master in de biomedische wetenschappen",
        "bachelor in de geneeskunde",
        "Educatieve master in de gezondheidswetenschappen"
    ],
    "Faculteit Industriële Ingenieurswetenschappen": [
        "bachelor in de industri\u00eble wetenschappen",
        "master in de industri\u00eble wetenschappen: nucleaire technologie",
        "master in de industri\u00eble wetenschappen: verpakkingstechnologie",
        "master in de industri\u00eble wetenschappen: chemie",
        "master in de industri\u00eble wetenschappen: elektromechanica",
        "Educatieve master in de wetenschappen en technologie",
        "master in de industri\u00eble wetenschappen: elektronica-ICT",
        "master in de industri\u00eble wetenschappen: bouwkunde",
        "master in de industri\u00eble wetenschappen: energie"
    ],
    "School voor Mobiliteitswetenschappen": [
        "bachelor in de mobiliteitswetenschappen",
        "master in de mobiliteitswetenschappen",
        "Master of Transportation Sciences"
    ],
    "Faculteit Rechten": [
        "bachelor in de rechten", "master in de rechten"
    ],
    "Faculteit Revalidatiewetenschappen": [
        "bachelor in de revalidatiewetenschappen en de kinesitherapie",
        "master in de revalidatiewetenschappen en de kinesitherapie"
    ],
    "Faculteit Wetenschappen": [
        "bachelor in de wiskunde", "bachelor in de informatica",
        "bachelor in de chemie", "bachelor in de biologie",
        "master in de informatica", "bachelor in de fysica",
        "Master of Statistics and Data Science"
    ],
    "School of Expert Education": [
        "Postgraduaat Stralingsdeskundige",
        "Postgraduaat Milieucoördinator - niveau A",
        "Postgraduaat Relatie- en Communicatiewetenschappen",
        "Postgraduaat Biogebaseerde en circulaire economie",
        "Postgraduaat Bedrijfskunde"
    ]
}


class UHasseltProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for UHasselt
    """
    name = 'uhasselt-programs'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}uhasselt_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        yield scrapy.Request(
            url=BASE_URL,
            callback=self.parse_main
        )

    def parse_main(self, response):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        list_progs = [(e['value'], e.text) for e in soup.find_all('select')[1].find_all('option')[1:]]

        BASE_DATA['__VIEWSTATE'] = response.xpath("//input[@id='__VIEWSTATE']/@value").get()
        BASE_DATA['__VIEWSTATEGENERATOR'] = response.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value").get()

        for program_id, program_name in list_progs:
            cur_data = BASE_DATA.copy()
            cur_data['beschridDDL$ctl00'] = program_id

            cycle = ''
            if 'bachelor' in program_name:
                cycle = 'bac'
            elif 'master' in program_name or 'Master' in program_name:
                cycle = 'master'
            elif 'Postgradua' in program_name:
                cycle = 'postgrad'

            # Faculty not crawlable so had to hard-code it
            faculties = []
            for f in FACULTIES_PROGRAMS:
                if program_name in FACULTIES_PROGRAMS[f]:
                    faculties = [f]
                    break

            base_dict = {
                "id": program_id,
                "name": program_name,
                "cycle": cycle,
                "faculties": faculties
            }

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

        ects = []
        if len(courses_ids) != 0:
            ects = response.xpath(f"{main_path}/td[5]/text()").getall()
            ects = [int(e) for e in ects if e.isnumeric()]
            # Some programs do not have a regular way of displaying ects... (some times 4th sometimes 5th column)
            if len(ects) != len(courses_ids):
                ects = [0]*len(courses_ids)

            # Remove duplicates
            courses_ids, ects = zip(*list(set(zip(courses_ids, ects))))

        cur_dict = {
            "campuses": [],  # Didn't find any info on campus
            "url": response.url,
            "courses": courses_ids,
            "ects": ects
        }
        yield {**base_dict, **cur_dict}
