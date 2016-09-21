# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class PageItem(scrapy.Item):
    uid = scrapy.Field()
    title =  scrapy.Field()
    url = scrapy.Field()
    path = scrapy.Field()
    folder = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
