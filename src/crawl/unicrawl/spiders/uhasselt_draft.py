import scrapy
import bs4

BASE_URL = 'https://uhintra03.uhasselt.be/studiegidswww/opleiding.aspx'

BASE_DATA = {
    '__EVENTTARGET': 'beschridDDL$ctl00',
    '__EVENTARGUMENT': '',
    '__LASTFOCUS': '',
    'ihTaal': '01',
    'ihBeschrid': '',
    'ihItemid': '',
    'ihVisible': '',
    'beschridAcjaar$ctl00': '2020',
}


def start_requests(self):
    yield scrapy.Request(
        url=BASE_URL,
        callback=self.parse_courses
    )


def parse_courses(self, response):
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    list_progs = [(e['value'], e.text) for e in soup.find_all('select')[1].find_all('option')[1:]]

    BASE_DATA['__VIEWSTATE'] = soup.find(id='__VIEWSTATE')['value']
    BASE_DATA['__VIEWSTATEGENERATOR'] = soup.find(id='__VIEWSTATEGENERATOR')['value']

    for prog, prog_name in list_progs:
        cur_data = BASE_DATA.copy()
        cur_data['beschridDDL'] = prog

        yield scrapy.http.FormRequest(
            BASE_URL,
            callback=self.parse_course,
            formdata=cur_data
        )


def parse_course(self, response):
    # Traitement d'une page
    pass