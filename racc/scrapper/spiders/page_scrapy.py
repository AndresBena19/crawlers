from bs4 import BeautifulSoup, Comment
from urlparse import urlparse
import scrapy
from scrapy.linkextractors import LinkExtractor
import re
import os.path
from scrapper.items import PageItem
from scrapy.spiders import SitemapSpider

class BasicPageSpider(SitemapSpider):

    name = 'page'
    allowed_domains = ["racc.edu"]
    sitemap_urls = ['http://www.racc.edu/sitemap.xml']

    def parse(self, response):

        # Parse url to obtain path
        parsed = urlparse(response.url)
        path = parsed.path
        folder = os.path.split(parsed.path)[0]

        # Map url
        mapurl = self.mapuid(path)

        # Beatifulsoup takes over the complete response html
        soup = BeautifulSoup(response.text, 'lxml')

        # Select the content node
        content = soup.find(id="content")
        if content is None:
            item = PageItem()
            item['uid'] = mapurl['uid']
            item['url'] = response.url
            item['path'] = path
            item['folder'] = folder
            yield item

        # remove html comments from it.
        for child in content:
            if isinstance(child, Comment):
                child.extract()

        # Remove the first submenu if it exists
        menus = content.select(".arrowList")
        if len(menus) > 0:
            menus[0].decompose()

        # Remove all top anchors
        top = content.select('a[href^="#top"]')
        for to in top:
            to.decompose()

        # Update urls
        for a in content.findAll('a'):
            if a['href'] == mapurl['oldurl']:
                a['href'] = mapurl['newurl']

        # Update image urls
        for img in content.findAll('img'):
            img['src'] = '/sites/default/files/imported' + folder + '/' + img['src']

        # Final basic page body as an string, remove linebreaks
        pattern = re.compile(r'\s+')
        body = "".join(str(item) for item in content.contents)
        body = re.sub(pattern, ' ', body).strip()

        item = PageItem()
        item['uid'] = mapurl['uid']
        item['url'] = response.url
        item['path'] = path
        item['folder'] = folder
        item['title'] = response.xpath('//h1/text()').extract_first()
        item['body'] = body

        yield item

    def mapuid(self,key):

        mapuid = {
            'not_exists' : {'uid': '0', 'oldurl': '', 'newurl' : ''},
            '/About/accreditations.aspx': {'uid': '25', 'oldurl': '/About/accreditations.aspx', 'newurl' : '/about-racc/accreditations'},
            '/About/board.aspx': {'uid': '26', 'oldurl': '/About/board.aspx','newurl': '/about-racc/board-trustees'},
            '/About/memberships.aspx': {'uid': '44', 'oldurl': '/About/memberships.aspx', 'newurl': '/about-racc/memberships'},
        }

        if key in mapuid:
            return mapuid[key]

        return mapuid['not_exists']

