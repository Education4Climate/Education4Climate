# -*- coding: utf-8 -*-
from abc import ABC

import scrapy

import config.settings as s
import config.utils as u

UCL_URL = f"https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-{s.YEAR}.html"


class UclSpider(scrapy.Spider, ABC):
    name = "ucl"
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/ucl_courses_{s.YEAR}.json',
    }

    def start_requests(self):
        base_url = UCL_URL
        yield scrapy.Request(url=base_url, callback=self.parse_main)

    def parse_main(self, response):
        for href in response.css(
                "a[href^='https://uclouvain.be/fr/catalogue-formations/']::attr(href)").getall():
            yield response.follow(href, self.parse_formation)

    def parse_formation(self, response):
        for href in response.css(f"li a[href^='/prog-{s.YEAR}']::attr(href)"):
            yield response.follow(href, self.parse_prog)

    def parse_prog(self, response):
        prog = response.url[21:]
        for href in response.css("li a[href^='" + prog + "-']::attr(href)"):
            yield response.follow(href, self.parse_prog_detail)

    def parse_prog_detail(self, response):
        for href in response.css(
                f"td.composant-ligne1 a[href^='https://uclouvain.be/cours-{s.YEAR}-']::attr(href)"):
            yield response.follow(href, self.parse_course)

    @staticmethod
    def parse_course(response):
        data = {
            'name': u.cleanup(response.css("h1.header-school::text").get()),
            'id': u.cleanup(response.css("span.abbreviation::text").get()),
            'year': u.cleanup(response.css("span.anacs::text").get()),
            'location': u.cleanup(response.css("span.location::text").get()),
            'teacher': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Enseignants')]]"
                               "/div/a/text())").getall()),
            'language': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Langue')]]"
                               "/div[@class='col-sm-10 fa_cell_2']/text())").get()),
            'prerequisite': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Préalables')]]"
                               "/div[@class='col-sm-10 fa_cell_2'])").get()),
            'theme': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Thèmes')]]"
                               "/div[@class='col-sm-10 fa_cell_2'])").get()),
            'goal': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Acquis')]]"
                               "/div[@class='col-sm-10 fa_cell_2'])").get()),
            'content': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Contenu')]]"
                               "/div[@class='col-sm-10 fa_cell_2'])").get()),
            'method': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Méthodes')]]"
                               "/div[@class='col-sm-10 fa_cell_2'])").get()),
            'evaluation': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Modes')]]"
                               "/div[@class='col-sm-10 fa_cell_2'])").get()),
            'other': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Autres')]]"
                               "/div[@class='col-sm-10 fa_cell_2'])").get()),
            'resources': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Ressources')]]"
                               "/div[@class='col-sm-10 fa_cell_2'])").get()),
            'biblio': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Bibliographie')]]"
                               "/div[@class='col-sm-10 fa_cell_2'])").get()),
            'faculty': u.cleanup(
                response.xpath("normalize-space(.//div[div[contains(text(),'Faculté')]]"
                               "/div[@class='col-sm-10 fa_cell_2'])").get()),
            'url': response.url
        }
        yield data

# Suppression du launcher artisanal, il ne faut pas utiliser ce genre de méthode ultra-roots...
# (il n'utilise alors pas le paramétrage du scraper)
# Pour lancer un crawler et le debugger sous Pycharm :
# Run / Edit configurations
# Choisir la configuration à modifier
# Switcher "Script path" par "Module name" et écrire : scrapy.cmdline
# Parameters : runspider unicrawl/spiders/{nom du script.py}
# Working directory : {chemin absolu de votre dossier unicrawl}\src\crawl
