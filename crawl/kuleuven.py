import scrapy
import bs4

from config.settings import YEAR

DOMAIN = 'https://onderwijsaanbod.kuleuven.be'
BASE_LINK = f'{DOMAIN}//opleidingen/e/#f=-1,-1,-1'
BASE_LINK_PROGS = f'{DOMAIN}/2020/opleidingen'


class KuleuvenSpider(scrapy.Spider):
    name = 'kuleuven'
    custom_settings = {
        'FEED_URI': f'../data/crawling-results/kuleuven_courses_{YEAR}.json',
    }

    def start_requests(self):
        yield scrapy.Request(BASE_LINK, self.parse)

    def parse(self, response):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        list_programmes = [
            (
                e.parent.parent.parent.parent.a.text,
                e.parent.parent.parent.a.span.text,
                e.a['href']
            )
            for e in soup.find_all('li', class_='taal_e')
        ]

        for faculty, cycle, relative_link in list_programmes:
            next_link_end = relative_link.split('/', 1)[1]
            next_link = f'{BASE_LINK_PROGS}/{next_link_end}'

            yield response.follow(
                next_link,
                self.parse_programme,
                cb_kwargs={'faculty': faculty, 'cycle': cycle}
            )

    def parse_programme(self, response, faculty, cycle):
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
                cb_kwargs={'faculty': faculty, 'cycle': cycle}
            )

    def parse_sub_programme(self, response, faculty, cycle):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        list_courses = [
            link['href']
            for link in soup.find(class_='programma__content').find_all('a')
            if 'syllabi' in link['href']
        ]

        for path in list_courses:
            next_link = f'{DOMAIN}{path}'
            year = path.split('/')[1]

            base_dict = {
                'year': f'{year}-{int(year) + 1}',
                'url': next_link,
                'faculty': faculty,
                'cycle': cycle,
                'formation': soup.find(class_='level_0').h1.text
            }

            yield response.follow(
                next_link,
                self.parse_course,
                cb_kwargs={'base_dict': base_dict}
            )

    def parse_course(self, response, base_dict):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        main = soup.find(id='main_container')
        titles = main.find(class_='breadcrumb_start')

        teach_list = [
            t.string.strip()
            for t in main.find(class_='docenten').find_all('a')
        ]

        # TODO : vérifier s'il n'est pas possible de remplir campus

        cur_dict = {
            'name': next(titles.a.next_siblings).strip(' \n>'),
            'id': main.find(class_='extraheading').string.strip(' \n()'),
            'teachers': teach_list,
            'ects': main.find(class_='studiepunten').string.split()[0],
            'content': main.find(class_='tab_content').p.string,
            'language': main.find(class_='taal').text.strip(' \n()'),
            'campus': None
        }

        yield {**base_dict, **cur_dict}
