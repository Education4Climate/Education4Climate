import scrapy

import config.settings as s


# import config.utils as u


class VUBSpider(scrapy.Spider):
    name = "vub"

    def start_requests(self):
        base_url = s.VUB_URL
        yield scrapy.Request(url=base_url, callback=self.parse_main)

    def parse_main(self, response):
        for link in response.xpath("//a[contains(@class, 'is-hyperlink')]/@href").getall():
            if link != '#':
                yield response.follow(link, self.parse_course)

    @staticmethod
    def parse_course(response):
        title1 = response.xpath("//div[@class='rd-inner-slide']/h3/text()")[0].extract().strip()
        title2 = response.xpath("//div[@class='rd-inner-slide']/h1/text()")[0].extract().strip()

        # TODO : Récupérer la data-key depuis le menu
        content_bloc = response.xpath(
            "//div[@data-key='tab_36996']/section[contains(@class, 'pg-text')]//p/text()")
        content = [c.extract() for c in content_bloc]

        data = {
            'name': f'{title1} {title2}'.title(),
            'id': response.url.rsplit('/', 1)[-1],
            'content': '\n'.join(content)
        }

        yield data