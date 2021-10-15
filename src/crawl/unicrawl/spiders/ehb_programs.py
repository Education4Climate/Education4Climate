# -*- coding: utf-8 -*-
from abc import ABC
from pathlib import Path

import scrapy
import json

from settings import YEAR, CRAWLING_OUTPUT_FOLDER

BASE_URL = "https://ects.ehb.be/#/training/1/{}"  # format is program code

acad_year = "{}".format(YEAR)

BASE_DATA = {
    "year": "{}-{}".format(acad_year, int(acad_year[-2:])+1),
    "language": "1",
    "faculty": "",
    "type": "",
    "text": "",
}


class EHBProgramSpider(scrapy.Spider, ABC):
    """
    Programs crawler for Erasmus Hogeschool Brussels

    METHOD:
    -------
    The website is based on Angular and contains dynamically loaded content.
    Therefore, plain scraping is not enough. The dynamically loaded data 
    is obtained by reproducing XHR Ajax POST requests.

    Campus information is missing in both courses and programs pages.
    """

    name = "ehb-programs"
    custom_settings = {
        'FEED_URI': Path(__file__).parent.absolute().joinpath(
            f'../../../../{CRAWLING_OUTPUT_FOLDER}ehb_programs_{YEAR}.json').as_uri()
    }

    def start_requests(self):

        # First, let's extract programs ids from Ajax POST request
        url = "https://desiderius.ehb.be/index.php?application=Ehb\Application\Ects\Ajax&go=FilterTrainings"
        yield scrapy.http.FormRequest(url, formdata=BASE_DATA, callback=self.parse_main)

    def parse_main(self, response):

        # The Ajax POST request returns a Json datafile
        programs_data = json.loads(response.body)
        # Collect all programs objects independently of their types
        programs = []
        for prog_type in programs_data["properties"]["type"].values():
            programs += prog_type["training"]
        
        for program in programs:

            print(program["type"])
            if 'bacheloropleiding' in program["type"]:
                cycle = 'bac'
            elif "Master" in program["type"]:
                cycle = 'master'
            elif "Postgraduaat" in program["type"]:
                cycle = 'postgrad'
            elif "Graduaat" in program["type"]:
                cycle = 'grad'
            else:
                cycle = 'other'

            base_dict = {
                "id": program["id"],
                "name": program["name"],
                "cycle": cycle,
                "faculties": [program["faculty"]],
                "campuses": [],
                "url": BASE_URL.format(program["id"])
            }

            # Each program can have several trajectories whose ids can be obtained via another Ajax POST request
            url = "https://desiderius.ehb.be/index.php?application=Ehb\Application\Ects\Ajax&go=Training"
            yield scrapy.http.FormRequest(url, formdata={"training": base_dict["id"], "language": "1"}, callback=self.parse_program, cb_kwargs={"base_dict": base_dict})

    def parse_program(self, response, base_dict):

        # The Ajax POST request returns a Json datafile
        program_data = json.loads(response.body)

        trajectories_ids = []
        for trajectory in program_data["properties"]["trajectories"]:
            trajectories_ids += [traj["id"] for traj in trajectory["trajectories"]]

        # Scrape courses sequentially from every trajectory and collect them in shared 'base_dict'
        if trajectories_ids:
            base_dict["courses"] = []
            base_dict["ects"] = []
            # Courses ids and ects can be obtained via yet another Ajax POST request
            url = "https://desiderius.ehb.be/index.php?application=Ehb\Application\Ects\Ajax&go=Trajectory"
            yield scrapy.http.FormRequest(url, formdata={"sub_trajectory": trajectories_ids[0], "language": "1"}, callback=self.parse_trajectories_recursively, cb_kwargs={"base_dict": base_dict, "trajectories_ids": trajectories_ids[1:]})

    def parse_trajectories_recursively(self, response, base_dict, trajectories_ids):

        # The Ajax POST request returns a Json datafile
        trajectory_data = json.loads(response.body)
        # Collect courses while avoiding duplicates
        courses_ids = [course["programme_id"] for course in trajectory_data["properties"]["courses"] if not(course["programme_id"] in base_dict["courses"])]
        courses_ects = [course["credits"] for course in trajectory_data["properties"]["courses"] if not(course["programme_id"] in base_dict["courses"])]
        base_dict["courses"] += courses_ids
        base_dict["ects"] += courses_ects

        # Parse the next program trajectory or yield final result
        if trajectories_ids:
            url = "https://desiderius.ehb.be/index.php?application=Ehb\Application\Ects\Ajax&go=Trajectory"
            yield scrapy.http.FormRequest(url, formdata={"sub_trajectory": trajectories_ids[0], "language": "1"},
                                          callback=self.parse_trajectories_recursively,
                                          cb_kwargs={"base_dict": base_dict, "trajectories_ids": trajectories_ids[1:]})
        else:
            yield base_dict
