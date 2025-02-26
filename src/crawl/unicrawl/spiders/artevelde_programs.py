# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL_1 = ("https://www.arteveldehogeschool.be/nl/opleidingen/categorie/{}/type/bachelor-227"
              "/type/bachelor-na-bachelor-230/type/graduaat-386/type/microdegrees-239/type/postgraduaat-233?page={}")
BASE_URL_2 = f"https://ects.arteveldehogeschool.be/ahsownapp/ects/ECTS.aspx?ac={YEAR}-{YEAR+1-2000}"

# Need to indicate the number of pages to visit for each faculty - to determine juste go on the url 1 and click on each
# faculty one after the other (if overestimated, should not affect the crawling)
FACULTIES = {
    'business-management-38': ["Business en Management", 3],
    "coaching-en-begeleiding-53": ["Coaching en Begeleiding", 1],
    "communicatie-media-en-design-41": ["Communicatie, Media en Design", 2],
    "gezondheid-en-zorg-44": ["Gezondhied en Zorg", 4],
    "hr-en-leiderschap-56": ["HR en Leiderschap", 1],
    "mens-en-samenleving-47": ["Mens en Samenleving", 2],
    "onderwijs-50": ["Onderwijs", 3]
}


# Not in programs map (so not in drop-down list https://ects.arteveldehogeschool.be/ahsownapp/ects/ECTS.aspx?ac=2024-25)
# - Accountancy - Fiscaliteit = Specialisation of Bedrijfsmanagement
# - Business & Languages (keuzetraject: Business Officer) = Specialisation of Organisatie en Management
# - Business & Languages (keuzetraject: Intercultural Relations) = Specialisation of Organisatie en Management
# - Digital Business = Organised by partner KdG Antwerp
# - Engels
# - Event & Project Management = Specialisation of Organisatie en Management
# - Financiën en Verzekeringen = Specialsation of Bedrijfsmanagement
# - Frans
# - Internationaal Ondernemen = Specialisation of Bedrijfsmanagement
# - Kmo-Management = Specialisation of Bedrijfsmanagement
# - Marketing = Specialisation of Bedrijfsmanagement
# - Rechtspraktijk = Specialisation of Bedrijfsmanagement
# - Spaans
# - Supply Chain Management = Specialisation of Bedrijfsmanagement
# - Audiovisual Design = Keuzetraject of Grafische en Digitale Media
# - Cross Media Design = Keuzetraject of Grafische en Digitale Media
# - Interactive Media Development = Keuzetraject of Grafische en Digitale Media
# - Print Media Technology = Keuzetraject of Grafische en Digitale Media
# - Toegepaste Informatica = Organised by partner KdG Antwerp
# - Audiologie = Missing ? Same as Logopedie en Audiologie ?
# - Logopedie = Missing ? Same as Logopedie en Audiologie ?
# - Basisverpleegkunde = Missing ?
# - European Stuttering Specialization = Missing ?
# - Management Centrale Sterilisatie Afdeling (CSA) = Not given in 2024-25
# - Medische Technologie = Missing ?
# - Perinatale coach = Missing ?
# - Toegepaste Gerontologie = In three partners school (AP Hogeschool, Karel de Grote Hogeschool en Arteveldehogeschool.)
# - Attest rooms-katholieke godsdienst kleuteronderwijs = Missing ?
# - Attest rooms-katholieke godsdienst lager onderwijs = Missing ?
# - Basiskennis bio-esthethiek = Missing ?
# - Basiskennis haartooi = Missing ?
# - Beleidsondersteuner = Missing ?
# - Lichamelijke opvoeding en Bewegingsrecreatie = Missing ?
# - Zorg in de klas = Missing ? Or microdegrees ?
# - Zorg voor de leerling = Missing ? Or microdegrees ?



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
    "Digitale Vormgeving": "Graduaat in de digitale vormgeving",
    "International Communication Management": "Bachelor of International Communication Management",
    "Journalistiek": "Bachelor in de journalistiek",
    "Programmeren": "Graduaat in het programmeren",
    "Conversational Design": "Postgraduaat Conversational Design",
    "Digital Content Creation en AI": "Postgraduaat Digital Content Creation",
    "Digital Marketing Communication": "Postgraduaat Digital Marketing Communication",
    "Experience Architect": "Postgraduaat Experience Architect",
    "Podcasting": "Postgraduaat Podcasting",
    "Ergotherapie": "Bachelor in de ergotherapie",
    "Logopedie en Audiologie": "Bachelor in de logopedie en de audiologie",
    "Mondzorg": "Bachelor in de mondzorg",
    "Palliatieve Zorg": "Postgraduaat Palliatieve zorg",
    "Podologie": "Bachelor in de podologie",
    "Verpleegkunde": "Bachelor in de verpleegkunde",
    "Vroedkunde": "Bachelor in de vroedkunde",
    "Vroedvrouw in de Eerste Lijn": "Postgraduaat De vroedvrouw in de eerste lijn",
    "Creatieve Therapie": "Bachelor in de creatieve therapie",
    "Creatief Coachen": "Postgraduaat Creatief coachen",
    "Acute Psychiatrische Zorg": "Postgraduaat acute psychiatrische zorg",
    "Toegepaste Psychologie": "Bachelor in de toegepaste psychologie",
    "Diabeteseducator": "Postgraduaat diabeteseducator",
    "Dysfagie": "Postgraduaat dysfagie",
    "Hippotherapie": "Postgraduaat hippotherapie",
    "Kaderopleiding Hoofdverpleegkundige": "Postgraduaat Kaderopleiding hoofdverpleegkundige",
    "Lactatiekunde": "Postgraduaat lactatiekunde",
    "Neurogene Communicatiestoornissen": "Postgraduaat neurogene communicatiestoornissen",
    "Neurologische Zorg": "Postgraduaat neurologische zorg",
    "Oncologie": "Postgraduaat oncologie",
    "Pediatrie en Neonatologie": "Postgraduaat pediatrie en neonatologie",
    "Kritieke pediatrie": "Postgraduaat Kritieke Pediatrie",
    "Stomatherapie en Wondzorg": "Postgraduaat stomatherapie en wondzorg",
    "Verpleegkundige in de Huisartsenpraktijk":
        "Postgraduaat verpleegkundige in huisartsenpraktijk",
    "Pedagogie van het Jonge Kind": "Bachelor in de pedagogie van het jonge kind",
    "Sociaal Werk": "Bachelor in het sociaal werk",
    "Informatiebeheer": "Graduaat in het informatiebeheer",
    "Maatschappelijk werk": "Graduaat in het maatschappelijk werk",
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
    "Freinet": "Postgraduaat Freinet",
    "Orthopedagogische Begeleiding": "Graduaat in de orthopedagogische begeleiding",
    "School of Branding" :"Postgraduaat School of Branding",
    "Mindfulnesstrainer": "Postgraduaat Mindfulnesstrainer",
    "Gecertificeerd accountant": "Postgraduaat Gecertificeerd Accountant"
}
# Note: not in the program description page
# Beleidsondersteuner
# Basiskennis haartooi
# Basiskennis bio-esthethiek
# Attest rooms-katholieke godsdienst kleuteronderwijs
# Attest rooms-katholieke godsdienst lager onderwijs



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

        yield scrapy.Request(BASE_URL_1.format(faculty_codes[0], 0), self.parse_faculties,
                             cb_kwargs={"faculty": faculty_codes[0],
                                        "remaining_faculties": faculty_codes[1:],
                                        "page_nb": 0,
                                        "programs_info": programs_info})

    def parse_faculties(self, response, faculty, remaining_faculties, page_nb, programs_info):

        all_programs_names = response.xpath("//h3/a[contains(@href, 'opleiding')]/text()").getall()
        all_programs_names = [name.strip(" \n") for name in all_programs_names]
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
            programs_info[program_name] = {"faculty": FACULTIES[faculty][0],
                                           # "campus": program_campus,
                                           "campuses": program_campuses,
                                           "cycle": program_cycle}

        # Check if we are at the last page:
        if page_nb < FACULTIES[faculty][1] - 1:
            page_nb += 1
            yield scrapy.Request(BASE_URL_1.format(faculty, page_nb), self.parse_faculties,
                                 cb_kwargs={"faculty": faculty,
                                            "remaining_faculties": remaining_faculties,
                                            "page_nb": page_nb,
                                            "programs_info": programs_info})
        # Iteratively crawl the other faculties
        elif len(remaining_faculties) != 0:
            yield scrapy.Request(BASE_URL_1.format(remaining_faculties[0], 0), self.parse_faculties,
                                 cb_kwargs={"faculty": remaining_faculties[0],
                                            "remaining_faculties": remaining_faculties[1:],
                                            "page_nb": 0,
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
                "campuses": programs_info[program_name]["campuses"],
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
