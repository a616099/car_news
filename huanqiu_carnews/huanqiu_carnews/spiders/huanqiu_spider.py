# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector
from huanqiu_carnews.items import HuanqiuCarnewsItem

class huanqiu_Spider(scrapy.Spider):
    name = "huanqiu"
    ba_url = lambda self, x:"http://www.huanqiuauto.com/index.php?caid=17&page=%d&searchword="%x
    start_urls = ["http://www.huanqiuauto.com/index.php?caid=17&page=1&searchword=",]

    # def start_requests(self):@class='znews_nav_scon']/div[@class='znews_nav_scon_l']/div[@class='pagelist']/div[@class='p_bar']/a[@class='p_pages']/text()").extract()
    def parse(self, response):
        sel = Selector(response)
        pages_x = sel.xpath("/html/body/div[@class='znews_nav_scon']/div[@class='znews_nav_scon_l']/div[@class='pagelist']/div[@class='p_bar']/a[@class='p_pages']/text()").extract()[0]
        pages_numb = pages_x.strip().split('/')[-1]

        for n in range(int(pages_numb)):
            urls = self.ba_url(n+1)
            yield scrapy.Request(urls, callback=self.parse_list_url)

    def parse_list_url(self, response):
        sel = Selector(response)
        list_urls = sel.xpath("/html/body/div[@class='znews_nav_scon']/div[@class='znews_nav_scon_l']/ul/li/h3/a/@href").extract()
        for url in list_urls:
            yield scrapy.Request(url, callback=self.parse_items)

    def parse_items(self, response):

        item = HuanqiuCarnewsItem()
        sel = Selector(response)
        item['news_title'] = sel.xpath("//h1/text()").extract_first()
        
        strings = sel.xpath("//div[@class='znews3_xx']/text()").extract_first().replace(u'\xa0', '')        

        time ,_other = strings.split(u'来源：')
        source , author = _other.split(u'编辑：')
        item['post_time'] = time
        item['source'] = source[:-5]
        item['keywords'] = ''
        item['summary'] = ''
        item['author'] = author[:-3]
        item['pic'] = sel.xpath("//div[@class='znews3_txt']//img/@src").extract()
        info = response.xpath("//div[@class='znews3_txt']")[0]
        item['text'] = info.xpath('string(.)').extract_first()
        item['subhead'] = ''
        item['comment'] = response.xpath("//div[@class='zvod_plli_t']/em/strong/text()").extract()[0]
        item['views'] = 0
        item['url'] = response.url
        
        yield item