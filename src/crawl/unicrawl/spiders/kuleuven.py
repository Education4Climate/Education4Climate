from abc import ABC

import bs4
import scrapy

from config.settings import YEAR

DOMAIN = 'https://onderwijsaanbod.kuleuven.be'
BASE_LINK = f'{DOMAIN}//opleidingen/e/#f=-1,-1,-1'
BASE_LINK_PROGS = f'{DOMAIN}/2020/opleidingen'
DICT_LANGUES = {
    'English': 'en',
    'Nederlands': 'nl',
    'Français': 'fr',
    'Español': 'es'
}


class KuleuvenSpider(scrapy.Spider, ABC):
    name = 'kuleuven'
    custom_settings = {
        'FEED_URI': f'../../data/crawling-output/kuleuven_courses_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(BASE_LINK, self.parse_main)

    def parse_main(self, response):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        list_campus = [
            (e['value'], e.text.strip())
            for e in soup.find(id='kulat_select').optgroup.find_all('option')
        ]

        list_programmes = [
            (
                cname,
                e.parent.parent.parent.parent.a.text,
                e.parent.parent.parent.a.span.text,
                e.a['href']
            )
            for campus, cname in list_campus
            for e in soup.find_all('li', class_=['taal_e', campus])
        ]

        for campus, faculty, cycle, relative_link in list_programmes:
            next_link_end = relative_link.split('/', 1)[1]
            next_link = f'{BASE_LINK_PROGS}/{next_link_end}'

            yield response.follow(
                next_link,
                self.parse_programme,
                cb_kwargs={'campus': campus, 'faculty': faculty, 'cycle': cycle}
            )

    def parse_programme(self, response, campus, faculty, cycle):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        list_sub_programmes = [
            e['href']
            for e in soup.find(id='side_container').find_all('a')
        ]

        for link in list_sub_programmes:
            cur_link_parent = response.request.url.rsplit('/', 1)[0]
            next_link = f'{cur_link_parent}/{link}'

            yield response.follow(
                next_link,
                self.parse_sub_programme,
                cb_kwargs={'campus': campus, 'faculty': faculty, 'cycle': cycle}
            )

    def parse_sub_programme(self, response, campus, faculty, cycle):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        list_courses = [
            link['href']
            for link in soup.find(class_='programma__content').find_all('a')
            if 'syllabi' in link['href']
        ]

        for path in list_courses:
            next_link = f'{DOMAIN}{path}'

            nom_formation = (
                soup.find(class_='level_0')
                    .h1
                    .text
                    .splitlines()[0]
                    .strip()
                    .rsplit(' (', 1)[0]
            )

            base_dict = {
                'year': path.split('/')[1],
                'url': next_link,
                'faculty': faculty,
                'cycle': cycle,
                'formation': nom_formation,
                'campus': campus,
            }

            yield response.follow(
                next_link,
                self.parse_course,
                cb_kwargs={'base_dict': base_dict}
            )

    @staticmethod
    def parse_course(response, base_dict):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        main = soup.find(id='main_container')
        titles = main.find(class_='breadcrumb_start')

        teach_list = [
            t.string.strip()
            for t in main.find(class_='docenten').find_all('a')
        ]

        content = '\n'.join([
            p.text.strip()
            for p in main.find(class_='tab_content').find_all('p')
            if p.text.strip()
        ])

        language = [
            lang.text.strip(' \n()')
            for lang in main.find_all('span', class_='taal')
        ]

        ects = [
            float(pts.string.split()[0])
            for pts in main.find(class_='studiepunten')
        ]

        # TODO : discuter la question de formation en tant que liste

        cur_dict = {
            'name': titles.text.split('>')[-1].strip(),
            'id': main.find(class_='extraheading').string.strip(' \n()'),
            'teachers': teach_list,
            'ects': ects,
            'content': content,
            'language': sorted(set(DICT_LANGUES.get(lang, lang) for lang in language))
        }

        yield {**base_dict, **cur_dict}
