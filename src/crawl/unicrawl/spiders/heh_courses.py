# -*- coding: utf-8 -*-
from pathlib import Path
from abc import ABC
from os import remove
from typing import Dict

import pandas as pd
import re
import scrapy

import urllib3
import pypdf

LANGUAGES_DICT = {
    "Français": 'fr',
    "Anglais": 'en',
    "Allemand": 'de',
    "Néerlandais": 'nl',
    "Italien": "it",
    "Espagnol": "es"
}

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

import logging
logging.getLogger().setLevel(logging.INFO)

BASE_URL = "https://www.heh.be/upload/ects/{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}heh_programs_{YEAR}.json')


def download_pdf(pdf_url: str) -> str:

    urllib3.disable_warnings()
    file_path = r"file.pdf"
    with urllib3.PoolManager() as http:
        r = http.request('GET', pdf_url)
        with open(file_path, 'wb') as fout:
            fout.write(r.data)
    return file_path


def extract_content(pdf_url: str, course_id: str) -> Dict:

    pdf_path = download_pdf(pdf_url)
    try:
        pdf_reader = pypdf.PdfReader(pdf_path)
        # Use two readers because some data is more accessible via one, and some via the other
        content = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            content += page.extract_text() + '\n'

        course_name = re.search(r"Intitulé de l'UE (.*)", content)[1]

        years = re.search(r"Année académique : (\d{4} - \d{4})", content)
        first_year = int(years[1].split(" -")[0]) if years else YEAR
        year = f'{first_year}-{first_year - 2000 + 1}'

        languages_lines = re.search(r"Langue d'enseignement([\s\S]*?)"
                                    r"Connaissances et compétences préalables", content, re.DOTALL)[1]
        languages = set(re.findall(r": (\w+)$", languages_lines, re.MULTILINE))
        languages = [LANGUAGES_DICT[l] for l in languages]

        teachers_lines = re.search(r"Enseignant\(s\)([\s\S]*?)Prérequis", content, re.DOTALL)[1]
        teachers = set(re.findall(r"([A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ']+ [A-ZÀ-ÖØ-Þ' ]+)$", teachers_lines, re.MULTILINE))
        teachers = sorted([(" ".join(teacher.title().split(" ")[1:]) + " " + teacher.split(" ")[0]).strip(" ")
                           for teacher in teachers])

        content_txt = re.search("(Contenu de (.*?)\n[\s\S]*?)Méthodes d'enseignement", content, re.DOTALL)
        content_txt = content_txt[1].strip("\n ") if content_txt else ''

        goals = re.search("Acquis d'apprentissage spécifiques\n([\s\S]*?)Contenu de", content, re.DOTALL)
        goals = goals[1].strip("\n ") if goals else ''

    except pypdf.errors.PdfStreamError:
        remove(pdf_path)
        return {}

    return {
        "id": course_id,
        "name": course_name,
        "year": year,
        "languages": languages,
        "teachers": teachers,
        "url": pdf_url,
        "content": content_txt,
        "goal": goals,
        "activity": '',
        "other": ''
    }


class HEHCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for HEH
    """

    name = 'heh-courses'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}heh_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):
        # Dummy call to make the whole thing work, not sure it is the best approach
        yield scrapy.Request('https://www.heh.be/', self.parse)

    @staticmethod
    def parse(response):

        courses_df = pd.read_json(open(PROG_DATA_PATH, "r"))[["courses", "courses_names", "courses_urls"]]
        courses_ids_list = courses_df["courses"].sum()
        courses_names_list = courses_df["courses_names"].sum()
        courses_urls_list = courses_df["courses_urls"].sum()

        courses_df = pd.DataFrame({'id': courses_ids_list, 'name': courses_names_list, 'url': courses_urls_list})
        courses_df = courses_df.drop_duplicates(subset='id')
        courses_df = courses_df.set_index("id").sort_index()

        for i, (idx, courses_ds) in enumerate(courses_df.iterrows()):

            url = BASE_URL.format(courses_ds['url'])
            base_dict = extract_content(url, idx)

            if base_dict != {}:
                yield base_dict
            else:

                yield {
                    "id": idx,
                    "name": courses_ds['name'],
                    "year": f"{YEAR}-{YEAR-2000+1}",
                    "languages": [],
                    "teachers": [],
                    "url": url,
                    "content": '',
                    "goal": '',
                    "activity": '',
                    "other": ''
                }
