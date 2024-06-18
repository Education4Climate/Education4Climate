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

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

import logging
logging.getLogger().setLevel(logging.INFO)

BASE_URL = "https://studiekiezer.ugent.be/{}/ministudiefiche/{}"
PROG_DATA_PATH = Path(__file__).parent.absolute().joinpath(
    f'../../../../{CRAWLING_OUTPUT_FOLDER}ugent_programs_{YEAR}.json')

LANGUAGE_DICT = {
    "Nederlands": 'nl',
    "Engels": 'en',
    "Frans": 'fr',
    "Chinees": 'cn',
    "Duits": 'de',
    'Japans': 'jp',
    "Hindi": 'hi',
    "Arabisch": 'ar',
    "Spaans": 'es',
    "Portugees": "pt",
    "Italiaans": 'it',
    "Russisch": 'ru',
    "Turks": 'tr',
    "Kroatisch": 'hr',
    "Lingala": 'ln',
    "Grieks": 'gr',
    "Afrikaans": 'za',
    "Sloveens": 'si',
    "Zweeds": 'se',
    "Bulgaars": 'bg',
    "Bosnisch": 'ba',
    "Deens": 'dk',
    "Ijslands": 'is',
    "Noors": 'no',
    "Koreaans": 'kr',
    "Servisch": 'rs'
}


def download_pdf(pdf_url: str) -> str:

    urllib3.disable_warnings()
    file_path = "file.pdf"
    with urllib3.PoolManager() as http:
        r = http.request('GET', pdf_url)
        with open(file_path, 'wb') as fout:
            fout.write(r.data)
    return file_path


def extract_content(pdf_url: str) -> Dict:

    # Download pdf and extract text
    pdf_path = download_pdf(pdf_url)
    try:
        pdf_reader = pypdf.PdfReader(pdf_path)
        content = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            content += page.extract_text() + '\n'

        course_id = re.compile(r'[A-Z]\d{6}').search(content)[0]
        course_name = re.compile(r'(.*)\s(\n)?\([A-Z]\d{6}\)').search(content)
        course_name = course_name[1].strip(" ") if course_name else ''

        year = re.compile(r'in academiejaar (\d{4}-\d{4})').search(content)
        year = year[1] if year else f'{YEAR}-{YEAR-2000+1}'

        languages = re.compile(r'Onderwijstalen\n([A-Za-z0-9\s\n\(\),äáàöôëéèï]+)'
                               r'\n(\(Goedgekeurd\)\n\n1\n\n\x0c)?Trefwoorden').search(content)
        languages = [LANGUAGE_DICT[lang] for lang
                     in languages[1].replace("1 (Goedgekeurd)" ,'').strip('\n').split(", ")] \
            if languages else []

        # Teachers
        teach_pattern = (r'Lesgevers in academiejaar 2023-2024([\s\S]*?)'
                         r'Aangeboden in onderstaande opleidingen in 2023-2024')
        # Extract the section listing teacher
        content_match = re.search(teach_pattern, content)
        teachers = []
        if content_match:
            # Extract teachers' names
            extracted_content = content_match.group(1).strip()
            name_pattern = r'(.*,\s\w+)'
            name_matches = re.findall(name_pattern, extracted_content)
            teachers = [match for match in name_matches]
        # teachers = teachers[1].split("\n") if teachers else []
        teachers = [t.replace(', ', ' ') for t in teachers]

        content_txt = re.search(r'Inhoud\n(.*?)\nBegincompetenties', content, re.DOTALL)
        content_txt = content_txt.group(1) if content_txt else ''

        goal = re.search(r'Situering\n(.*?)\nInhoud', content, re.DOTALL)
        goal = goal.group(1) if goal else ''

    except pypdf.errors.PdfStreamError:
        remove(pdf_path)
        return {}

    remove(pdf_path)

    return {
        "id": course_id,
        "name": course_name,
        "year": year,
        "languages": languages,
        "teachers": teachers,
        "url": pdf_url,
        "content": content_txt,
        "goal": goal,
        "activity": '',
        "other": ''
}


class UGentCourseSpider(scrapy.Spider, ABC):
    """
    Courses crawler for UGent
    """

    name = 'ugent-courses'
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ugent_courses_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        courses_df = pd.read_json(open(PROG_DATA_PATH, "r"))[["courses", "courses_names",
                                                              "courses_languages", "courses_urls"]]
        courses_ids_list = courses_df["courses"].sum()
        courses_names_list = courses_df["courses_names"].sum()
        courses_lang_list = courses_df["courses_languages"].sum()
        courses_urls_list = courses_df["courses_urls"].sum()

        courses_df = pd.DataFrame({'id': courses_ids_list, 'name': courses_names_list,
                                   'languages': courses_lang_list, 'url': courses_urls_list})
        courses_df = courses_df.drop_duplicates(subset='id')

        for _, courses_ds in courses_df.iterrows():

            # Retrieve some info in case the pdf reading does not work
            languages = courses_ds['languages'].split(',')
            languages = [] if languages == [''] else languages

            year = courses_ds['url'].split("/")[0]
            nbs = "/".join(courses_ds['url'].split("/")[1:])
            yield scrapy.Request(url=BASE_URL.format(year, nbs),
                                 callback=self.parse_course_info,
                                 cb_kwargs={"course_id": courses_ds['id'],
                                            "course_name": courses_ds['name'],
                                            "languages": languages})

    @staticmethod
    def parse_course_info(response, course_id, course_name, languages):

        response_json = response.json()

        # Course description
        base_dict = {}
        if 'studieficheUrlNL' in response_json:
            content_link = response_json['studieficheUrlNL']
            content_link = response.url.split("ministudiefiche")[0] + content_link.strip("../")
            base_dict = extract_content(content_link)
        else:
            content_link = response.url

        if 'id' in base_dict.keys():
            yield base_dict
        else:
            # If pdf extraction failed still save some information
            yield {
                "id": course_id,
                "name": course_name,
                "year": f"{YEAR}-{int(YEAR) + 1}",
                "languages": languages,
                "teachers": [],
                "url": content_link,
                "content": "",
                "goal": '',
                "activity": '',
                "other": ''
            }
