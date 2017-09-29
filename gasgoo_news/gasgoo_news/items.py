# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GasgooNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    news_title = scrapy.Field()
    post_time = scrapy.Field()
    source = scrapy.Field()
    keywords = scrapy.Field()
    summary = scrapy.Field()
    author = scrapy.Field()
    pic = scrapy.Field()
    text = scrapy.Field()
    subhead = scrapy.Field()
    comment = scrapy.Field()
    view = scrapy.Field()
