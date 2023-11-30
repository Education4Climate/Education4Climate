# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL_1 = ("https://www.arteveldehogeschool.be/nl/opleidingen/categorie/{}/type/bachelor-227"
              "/type/bachelor-na-bachelor-230/type/graduaat-386/type/microdegrees-239/type/postgraduaat-233")
BASE_URL_2 = f"https://ects.arteveldehogeschool.be/ahsownapp/ects/ECTS.aspx?ac={YEAR}-{YEAR+1-2000}"

FACULTIES = {
    'business-management-38': "Business en Management",
    "coaching-en-begeleiding-53": "Coaching en Begeleiding",
    "communicatie-media-en-design-41": "Communicatie, Media en Design",
    "gezondheid-en-zorg-44": "Gezondhied en Zorg",
    "hr-en-leiderschap-56": "HR en Leiderschap",
    "mens-en-samenleving-47": "Mens en Samenleving",
    "onderwijs-50": "Onderwijs"
}

# Not working for Gecertificeerd accountant, Management Centrale Sterilisatie Afdeling (CSA)

PROGRAMS_MAP = {
    "Bedrijfsmanagement": "Bachelor in het bedrijfsmanagement",
    "Informatiebeheer: Bibliotheek en Archief": "Graduaat in het informatiebeheer", # TODO: maybe remove
    "European Clinical Specialization in Fluency Disorders": "Postgraduaat Fluency Disorders",
    "International Business Management": "Bachelor of International Business Management",
    "Organisatie en Management": "Bachelor in organisatie & management",
    "Accounting Administration": "Graduaat in de accounting administration",
    "Marketing- en Communicatiesupport": "Graduaat in de marketing- en communicatiesupport",
    "Digital Business Transformation": "Postgraduaat Digital Business Transformation",
    "Human Resources Management": "Postgraduaat HRM",
    "Inspirerend Coachen": "Postgraduaat Inspirerend coachen",
    "Intercultureel werken en coachen": "Postgraduaat intercultureel werken en coachen",
    "Leiderschap": "Postgraduaat Leiden en begeleiden",
    "Ondernemen met Impact": "Postgraduaat Ondernemen met impact",
    "Rouw- en Verliesconsulent": "Postgraduaat Rouw- en verliesconsulent",
    "Supply Chain Management & Business Analytics":
        "Postgraduaat Supply Chain Management & Business Analytics",
    "The Human-Centered Organisation": "Postgraduaat The Human-Centered Organisation",
    "Autisme": "Postgraduaat autisme",
    "Leerstoornissen": "Postgraduaat leerstoornissen",
    "Leescoach": "Postgraduaat Leescoach",
    "Communicatiemanagement": "Bachelor in het communicatiemanagement",
    "Communicatie": "Bachelor in de communicatie",
    "Grafische en Digitale Media": "Bachelor in de grafische en digitale media",
    "International Communication Management": "Bachelor of International Communication Management",
    "Journalistiek": "Bachelor in de journalistiek",
    "Programmeren": "Graduaat in het programmeren",
    "Conversational Design": "Postgraduaat Conversational Design",
    "Digital Content Creation": "Postgraduaat Digital Content Creation",
    "Digital Marketing Communication": "Postgraduaat Digital Marketing Communication",
    "Experience Architect": "Postgraduaat Experience Architect",
    "Podcasting": "Postgraduaat Podcasting",
    "Ergotherapie": "Bachelor in de ergotherapie",
    "Logopedie en Audiologie": "Bachelor in de logopedie en de audiologie",
    "Mondzorg": "Bachelor in de mondzorg",
    "Podologie": "Bachelor in de podologie",
    "Verpleegkunde": "Bachelor in de verpleegkunde",
    "Vroedkunde": "Bachelor in de vroedkunde",
    "Creatieve Therapie": "Bachelor in de creatieve therapie",
    "Acute Psychiatrische Zorg": "Postgraduaat acute psychiatrische zorg",
    "Diabeteseducator": "Postgraduaat diabeteseducator",
    "Dysfagie": "Postgraduaat dysfagie",
    "Hippotherapie": "Postgraduaat hippotherapie",
    "Kaderopleiding Hoofdverpleegkundige": "Postgraduaat Kaderopleiding hoofdverpleegkundige",
    "Lactatiekunde": "Postgraduaat lactatiekunde",
    "Neurogene Communicatiestoornissen": "Postgraduaat neurogene communicatiestoornissen",
    "Neurologische Zorg": "Postgraduaat neurologische zorg",
    "Oncologie": "Postgraduaat oncologie",
    "Pediatrie en neonatologie": "Postgraduaat pediatrie en neonatologie",
    "Stomatherapie en wondzorg": "Postgraduaat stomatherapie en wondzorg",
    "Verpleegkundige in de huisartsenpraktijk":
        "Postgraduaat verpleegkundige in huisartsenpraktijk",
    "Pedagogie van het Jonge Kind": "Bachelor in de pedagogie van het jonge kind",
    "Sociaal Werk": "Bachelor in het sociaal werk",
    "Informatiebeheer": "Graduaat in het informatiebeheer",
    "Maatschappelijk werk": "Graduaat in het maatschappelijk werk",
    "Orthopedagogische Begeleiding": "Graduaat in de orthopedagogische begeleiding",
    "Sociaal-Cultureel Werk": "Graduaat in het sociaal-cultureel werk",
    "Tolk Vlaamse Gebarentaal": "Graduaat in de tolk Vlaamse Gebarentaal",
    "Contextuele en Systemische Counseling": "Postgraduaat Contextuele en systemische counseling",
    "Politisering in het Sociaal Werk": "Postgraduaat Politisering in het sociaal werk",
    "Educatieve Bachelor Kleuteronderwijs": "Educatieve bachelor (Ba) in het kleuteronderwijs",
    "Educatieve Bachelor Lager Onderwijs":
        "Educatieve bachelor in het onderwijs: lager onderwijs",
    "Educatieve Bachelor Secundair Onderwijs": "Educatieve bachelor in het secundair onderwijs",
    "Verkorte Educatieve Bachelor Secundair Onderwijs":
        "Educatieve bachelor in het onderwijs: secundair onderwijs (verkort)",
    "Educatief Graduaat Secundair Onderwijs":
        "Educatieve graduaatsopleiding in het secundair onderwijs",
    "Buitengewoon Onderwijs": "Bachelor in het onderwijs : buitengewoon onderwijs",
    "Schoolontwikkeling": "Bachelor in het onderwijs : schoolontwikkeling",
    "Zorgverbreding en Remediërend Leren":
        "Bachelor in het onderwijs  : zorgverbreding en remediërend leren",
    "Zorgleraar": "Postgraduaat Zorgleraar",
    "International Organisation and Management":
        "Bachelor of International Organisation & Management",
    "International Graphic and Digital Media":
        "Bachelor of International Graphic and Digital Media",
    "Transport en Logistiek": "Graduaat in het transport en de logistiek",
    "Diversiteitssensitief Werken, Communiceren en Leiden":
        "Postgraduaat Diversiteitssensitief werken, communiceren en leiden",
    "International Journalism": "Bachelor of International Journalism",
    "Creatieve Therapie: Bijkomend Medium": "Postgraduaat Creatieve Therapie: bijkomend medium",
    "Freinet": "Postgraduaat Freinet"
}

BASE_DATA = {
    "__EVENTTARGET": "ctl00$contentPlaceHolder$extendedSearchOLODS$btnZoekOpleidingsonderdelen",
    "__EVENTARGUMENT": "",
    "__LASTFOCUS": "",
    "ctl00_contentPlaceHolder_treeViewOLODS_treeViewOpleidingsonderdelen_ExpandState": "",
    "ctl00_contentPlaceHolder_treeViewOLODS_treeViewOpleidingsonderdelen_SelectedNode": "",
    "ctl00_contentPlaceHolder_treeViewOLODS_treeViewOpleidingsonderdelen_PopulateLog": "",
    "ctl00$contentPlaceHolder$extendedSearchOLODS$ddlAcademiejaar": f"{YEAR}-{YEAR+1-2000}",
    "ctl00$contentPlaceHolder$extendedSearchOLODS$ddlOpleiding": "",
    "ctl00$contentPlaceHolder$extendedSearchOLODS$rbtnListRaadplegen": "0",
}


class ArteveldeProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Artevelde Hogeschool
    """

    name = "artevelde-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}artevelde_programs_{YEAR}.json')
    }

    def start_requests(self):

        programs_info = {}
        faculty_codes = list(FACULTIES.keys())
        yield scrapy.Request(BASE_URL_1.format(faculty_codes[0]), self.parse_faculties,
                             cb_kwargs={"faculty": faculty_codes[0],
                                        "remaining_faculties": faculty_codes[1:],
                                        "programs_info": programs_info})

    def parse_faculties(self, response, faculty, remaining_faculties, programs_info):

        all_programs_names = response.xpath("//h3/a[contains(@href, 'opleiding')]/text()").getall()
        all_programs_names = [name.strip(" \n") for name in all_programs_names]
        print(all_programs_names)
        # Remove subprograms
        program_names = []
        for program_name in all_programs_names:
            request_text = f"//div[div[h3[a[contains(text(), \'{program_name}\')]]]]" \
                           f"//div[@class='field field-name-course-subtype']"
            subprogram_b = response.xpath(request_text).get()
            if not subprogram_b:
                program_names += [program_name]

        # Campus
        programs_campuses = []
        for program_name in program_names:
            request_text = f"//article[div[header[h3[a[contains(text(), \'{program_name}\')]]]]]" \
                           f"//div[@class='field--campus field']//dd/text()"
            programs_campuses += [response.xpath(request_text).getall()]
            # if campus and 'Campus' in campus:
            #     programs_campus += ["Campus " + campus.split("Campus ")[1].strip(", ")]
            # else:
            #     programs_campus += []

        # Cycle
        programs_cycle = []
        for program_name in program_names:
            request_text = f"//h3[a[contains(text(), \'{program_name}\')]]//following::div[1]/text()"
            cycle = response.xpath(request_text).get()
            if cycle is not None and 'bachelor' in cycle.lower():
                cycle = 'bac'
            elif 'postgraduaat' in cycle.lower():
                cycle = 'postgrad'
            elif 'graduaat' in cycle.lower():
                cycle = 'grad'
            else:
                cycle = 'other'
            programs_cycle += [cycle]

        # Associate faculty
        for program_name, program_campuses, program_cycle in zip(program_names, programs_campuses, programs_cycle):
            programs_info[program_name] = {"faculty": FACULTIES[faculty],
                                           # "campus": program_campus,
                                           "campuses": program_campuses,
                                           "cycle": program_cycle}

        # Iteratively crawl the other faculties
        if len(remaining_faculties) != 0:
            yield scrapy.Request(BASE_URL_1.format(remaining_faculties[0]), self.parse_faculties,
                                 cb_kwargs={"faculty": remaining_faculties[0],
                                            "remaining_faculties": remaining_faculties[1:],
                                            "programs_info": programs_info})
        else:
            yield scrapy.Request(BASE_URL_2, self.parse_programs, cb_kwargs={"programs_info": programs_info})

    def parse_programs(self, response, programs_info):

        programs_name_select = response.xpath("//select[contains(@name, 'Opleiding')]/option/text()").getall()
        programs_name_select = [" (".join(n.split(" (")[:-1]) for n in programs_name_select]
        programs_id_select = response.xpath("//select[contains(@name, 'Opleiding')]/option/@value").getall()
        select_name_id_map = dict(zip(programs_name_select, programs_id_select))

        BASE_DATA['__VIEWSTATE'] = response.xpath("//input[@id='__VIEWSTATE']/@value").get()
        BASE_DATA['__VIEWSTATEGENERATOR'] = response.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value").get()
        BASE_DATA['__EVENTVALIDATION'] = response.xpath("//input[@id='__EVENTVALIDATION']/@value").get()

        for program_name in programs_info.keys():

            if program_name not in PROGRAMS_MAP:
                print(f"{program_name} was not in PROGRAM_MAP")
                continue
            full_name = PROGRAMS_MAP[program_name]
            program_id_url = select_name_id_map[full_name]
            program_id = program_id_url.split(";")[1]

            cur_data = BASE_DATA.copy()
            cur_data['ctl00$contentPlaceHolder$extendedSearchOLODS$ddlOpleiding'] = program_id_url

            base_dict = {
                "id": program_id,
                "name": full_name,
                "cycle": programs_info[program_name]["cycle"],
                "faculties": [programs_info[program_name]["faculty"]],
                "campuses": [programs_info[program_name]["campuses"]],
                "url": BASE_URL_2
            }

            yield scrapy.http.FormRequest(
                BASE_URL_2,
                callback=self.parse_courses,
                formdata=cur_data,
                cb_kwargs={'base_dict': base_dict}
            )

    @staticmethod
    def parse_courses(response, base_dict):

        courses_links = response.xpath("///a[contains(@class, 'fancybox')]/@href").getall()
        courses_codes = [link.split("?")[1] for link in courses_links]
        courses_codes = [str(c.split("&b=")[0].strip("a=")) for c in courses_codes]
        # TODO: check b=1&c=1 always true
        # WARNING: no courses for freinet and leescoach
        print(base_dict['name'])
        print(courses_codes)

        base_dict["courses"] = courses_codes
        base_dict["ects"] = []

        yield base_dict
