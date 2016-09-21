import scrapy
from bs4 import BeautifulSoup, Comment
import re

class NewsSpider(scrapy.Spider):

    name = 'news'
    start_urls = ['http://racc.edu/News/default.aspx']

    def parse(self, response):

        # Beatifulsoup takes over the complete response html
        soup = BeautifulSoup(response.text, 'lxml')
        content = soup.find(id="content")

        # remove html comments from it.
        for child in content:
            if isinstance(child, Comment):
                child.extract()

        x = 0
        for art in content.findAll('article'):

            body = art.span
            if body is None:
                body = ''
            else:
                pattern = re.compile(r'\s+')
                body = "".join(str(item) for item in body.contents)
                body = re.sub(pattern, ' ', body).strip()

            x += 1

            yield {
                'id': x,
                'title': art.h2.get_text(),
                'excerpt': art.p.get_text(),
                'body': '<p>' + art.p.get_text().encode("UTF-8") + '</p>' + body
            }