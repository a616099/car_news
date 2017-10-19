# -*- coding: utf-8 -*-

import scrapy, re, hashlib, html, json, datetime
from scrapy.selector import Selector
from huanqiu_carnews.items import HuanqiuCarnewsItem
from huanqiu_carnews.cutword import cutword
from scrapy.conf import settings

class huanqiu_Spider(scrapy.Spider):
    name = "huanqiu"
    ba_url = lambda self, x:"http://www.huanqiuauto.com/index.php?caid=17&page=%d&searchword="%x
    start_urls = ["http://www.huanqiuauto.com/index.php?caid=17&page=1&searchword=",]

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

    # def start_requests(self):
    #     url = 'http://www.huanqiuauto.com/news/20171016/879039_1.html'
    #     yield scrapy.Request(url, callback=self.parse_items)

    def parse_items(self, response):

        item = {}
        sel = Selector(response)
        item['news_title'] = sel.xpath("//h1/text()").extract_first()   

        try:
            strings = sel.xpath("//div[@class='znews3_xx']/text()").extract_first().replace(u'\xa0', '')
            time ,_other = strings.split(u'来源：')
            source , author = _other.split(u'编辑：')
            item['source'] = source[:-5]
            item['author'] = author[:-3]
        except:
            item['source'] = ''
            item['author'] = ''
        item['post_time'] = strings.split(u'来源：')[0]
        item['keywords'] = ''
        item['summary'] = ''
        pic_urls = sel.xpath("//div[@class='znews3_txt']//img/@src").extract()

        text_body = sel.xpath("//div[@class='znews3_txt']").extract_first()
        html_body = html.unescape(text_body)
        path_md5 = hashlib.sha1(response.url.encode(encoding="utf-8")).hexdigest()
        pic = []
        item['pic'] = pic_urls
        for url in pic_urls:
            image_guid = hashlib.sha1(url.encode(encoding="utf-8")).hexdigest()
            pic.append({
                    'image_guid':image_guid,
                    'pic_url':url,
                        })
            if url in html_body:
                html_body = html_body.replace(url, "%s\%s"%(path_md5,image_guid))

        item['html_file'] = html_body
        item['pic_path'] = {'pic':pic,
                            'pic_path':path_md5,
                            }

        info = response.xpath("//div[@class='znews3_txt']")[0]
        item['subhead'] = ''
        item['url'] = response.url
        item['url_md5'] = path_md5

        text = info.xpath('string(.)').extract_first().strip() 
        if text:
            item['text'] = text
            item['text_sta'] = cutword(text)
        else:
            item['text'] = ''
            item['text_sta'] = ''
        now = datetime.datetime.now()
        item['collect_date'] = now.strftime("%Y-%m-%d")
        yield item