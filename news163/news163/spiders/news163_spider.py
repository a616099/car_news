# -*- coding: utf-8 -*-

import scrapy, re, hashlib, html
from scrapy.selector import Selector
from news163.items import News163Item
from scrapy.conf import settings

class news163_Spider(scrapy.Spider):

    name = 'news163'

    def start_requests(self):

        urls1 = [
            "http://auto.163.com/special/2016nauto/#subtab",
        ]
        for u in urls1:
            yield scrapy.Request(url=u, callback=self.parse_xinche, dont_filter=True)
        urls2 = [
            "http://auto.163.com/special/gongsixinwen/",
        ]
        for u in urls2:
            yield scrapy.Request(url=u, callback=self.gongsixinwen, dont_filter=True)
        urls3 = [
            "http://auto.163.com/special/0008280U/08news_more.html",
            "http://auto.163.com/special/shangyongche/",
            "http://auto.163.com/special/00084K25/qichezhaohui.html",
        ]
        for u in urls3:
            yield scrapy.Request(url=u, callback=self.hangye, dont_filter=True)
        urls4 = [
            "http://auto.163.com/special/00083T0B/spy_photos.html",
            "http://auto.163.com/special/00083U3Q/auto_ctfy.html",
            "http://auto.163.com/special/0008280U/yc_zhuanti.html",
            "http://auto.163.com/special/0008280U/yp_ycxc.html",
            "http://auto.163.com/special/0008280U/yp_lt.html",
            "http://auto.163.com/special/cxmore/",
            "http://auto.163.com/special/ypdzhmore/",
            "http://auto.163.com/special/0008280U/yp_zsgz.html",
        ]
        for u in urls4:
            yield scrapy.Request(url=u, callback=self.yongche, dont_filter=True)


    def parse_xinche(self, response):
        sel = Selector(response)
        url_a = sel.xpath("//div[@id='auto_pull_wrap']/div[@class='auto_channel_pages']/span/@href").extract()
        url_b = sel.xpath("//div[@id='auto_pull_wrap']/div[@class='auto_channel_pages']/a/@href").extract()[1:-1]
        for url in url_a+url_b:
            yield scrapy.Request(url=url, callback=self.xinche_urls, dont_filter=True)

    def gongsixinwen(self, response):
        sel = Selector(response)
        urls = sel.xpath("//div[@class='auto_channel_pages']/a/@href").extract()[1:-1]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.gongsixinwen_urls, dont_filter=True)

    def hangye(self, response):
        sel = Selector(response)
        urls = sel.xpath("//div[@class='pages']/a/@href").extract()[1:-1]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.hangye_urls, dont_filter=True)
    def yongche(self, response):
        sel = Selector(response)
        urls = sel.xpath("//div[@class='pages']/a/@href").extract()[1:-1]
        if urls:
            for url in urls:
                yield scrapy.Request(url=url, callback=self.yongche_urls, dont_filter=True)
        else:
            yield scrapy.Request(url=response.url, callback=self.yongche_urls, dont_filter=True)

    def xinche_urls(self, response):
        sel = Selector(response)
        con = sel.xpath("//div[@id='auto_pull_dataset']/div/a[@class='item-pic']/@href").extract()
        for n in con:
            yield scrapy.Request(url=n, callback=self.parse_items, dont_filter=True)

    def gongsixinwen_urls(self, response):
        sel = Selector(response)
        con = sel.xpath("//div[@class='am_bd']/ul/li/a/@href").extract()
        for n in con:
            yield scrapy.Request(url=n, callback=self.parse_items, dont_filter=True)

    def hangye_urls(self, response):
        sel = Selector(response)
        con = sel.xpath("//div[@class='content']/ul/li/a/@href").extract()
        for n in con:
            yield scrapy.Request(url=n, callback=self.parse_items, dont_filter=True)

    def yongche_urls(self, response):
        sel = Selector(response)
        con = sel.xpath("//div[@class='content']/ul/li/a/@href").extract()
        for n in con:
            yield scrapy.Request(url=n, callback=self.parse_items, dont_filter=True)

    def parse_items(self, response):

        item = News163Item()
        sel = Selector(response)
        if response.xpath("//div[@class='post_content post_area clearfix']"):
            item['news_title'] = sel.xpath("//div[@id='epContentLeft']/h1/text()").extract_first()
            item['post_time'] = sel.xpath("//div[@id='epContentLeft']/div[@class='post_time_source']/text()").extract_first().strip()[:-4]
            item['source'] = sel.xpath("//div[@id='epContentLeft']/div[@class='post_time_source']/a/text()").extract_first().strip()
            try:
                item['summary'] = sel.xpath("//div[@class='post_desc']/text()").extract_first().strip()
            except:
                item['summary'] = ''
            text = ''
            for n in sel.xpath("//div[@id='endText']/p//text()").extract():
                n.replace(u'\xa0', '')
                text += n
            text.replace(u'\xa0', '')
            try:
                item['author'] = sel.xpath("//div[@id='endText']/div/span/text()").extract_first().split(u'作者：')[-1]
            except:
                item['author'] = ''
            item['pic'] = sel.xpath("//div[@id='endText']//img/@src").extract()
            item['keywords'] = ''
            item['text'] = text
            item['subhead'] = ''
            text_body = sel.xpath("//div[@id='endText']").extract_first()
            html_body = html.unescape(text_body)
            path_md5 = hashlib.sha1(response.url.encode(encoding="utf-8")).hexdigest()
            pic = []
            for url in item['pic']:
                image_guid = hashlib.sha1(url.encode(encoding="utf-8")).hexdigest()
                pic.append({
                        'image_guid':image_guid,
                        'pic_url':url,
                            })
                if url in html_body:
                    html_body = html_body.replace(url, "%s\%s\%s"%(settings['IMAGES_STORE'],path_md5,image_guid))

            item['pic_path'] = {'pic':pic,
                                'pic_path':path_md5,
                                        }
            item['html_file'] = html_body
            
            
            item['url'] = response.url

            yield item
        elif response.xpath("//div[@class='ep-content-bg clearfix']"):
            item['news_title'] = sel.xpath("//h1[@id='h1title']/text()").extract_first()
            if sel.xpath("//div[@class='ep-info cDGray']/div[@class='left']/text()").extract_first():
                item['post_time'] = sel.xpath("//div[@class='ep-info cDGray']/div[@class='left']/text()").extract_first().strip()[:-4]
                item['source'] = sel.xpath("//div[@class='ep-info cDGray']/div[@class='left']/a/text()").extract_first()
            elif sel.xpath("//div[@class='ep-time-soure cDGray']/div[@class='left']/text()").extract_first():
                item['post_time'] = sel.xpath("//div[@class='ep-time-soure cDGray']/div[@class='left']/text()").extract_first().strip()[:-4]
                item['source'] = sel.xpath("//div[@class='ep-time-soure cDGray']/div[@class='left']/a/text()").extract_first()
            else:
                item['post_time'] = ''
                item['source'] = ''
            try:
                item['summary'] = sel.xpath("//p[@class='ep-summary']/text()").extract_first()
            except:
                item['summary'] = ''
            item['author'] = ''
            item['pic'] = sel.xpath("//div[@id='endText']/p/img/@src").extract()
            item['keywords'] = ''
            text = ''
            for n in sel.xpath("//div[@id='endText']/p//text()").extract():
                n.replace(u'\xa0', '')
                text += n
            text.replace(u'\xa0', '')
            item['text'] = text
            item['subhead'] = ''
            text_body = sel.xpath("//div[@id='endText']").extract_first()
            html_body = html.unescape(text_body)
            path_md5 = hashlib.sha1(response.url.encode(encoding="utf-8")).hexdigest()
            pic = []
            for url in item['pic']:
                image_guid = hashlib.sha1(url.encode(encoding="utf-8")).hexdigest()
                pic.append({
                        'image_guid':image_guid,
                        'pic_url':url,
                            })
                if url in html_body:
                    html_body = html_body.replace(url, "%s\%s\%s"%(settings['IMAGES_STORE'],path_md5,image_guid))

            item['pic_path'] = {'pic':pic,
                                'pic_path':path_md5,
                                        }
            item['html_file'] = html_body

            item['url'] = response.url

            yield item
        elif response.xpath("//div[@class='endContent']"):
            item['news_title'] = sel.xpath("//h1[@id='h1title']/text()").extract_first()
            if sel.xpath("//div[@class='endContent']/span[@class='info']/text()").extract_first():
                item['post_time'] = sel.xpath("//div[@class='endContent']/span[@class='info']/text()").extract_first().strip()[:-4]
                item['source'] = sel.xpath("//div[@class='endContent']/span[@class='info']/a/text()").extract_first()
            elif sel.xpath("//div[@class='endContent bg_endPage_Lblue']/span[@class='info']/text()").extract_first():
                item['post_time'] = sel.xpath("//div[@class='endContent bg_endPage_Lblue']/span[@class='info']/text()").extract_first().strip()[:-4]
                item['source'] = sel.xpath("//div[@class='endContent bg_endPage_Lblue']/span[@class='info']/a/text()").extract_first() 
            else:
                item['post_time'] = ''  
                item['source'] = ''            
            try:
                item['summary'] =  sel.xpath("//div[@class='endContent']/p[@class='summary']/text()").extract_first()
            except:
                item['summary'] = ''
            item['author'] = ''
            item['pic'] = sel.xpath("//div[@id='endText']/p/img/@src").extract()
            item['keywords'] = ''
            text = ''
            for n in sel.xpath("//div[@id='endText']/p//text()").extract():
                n.replace(u'\xa0', '')
                text += n
            text.replace(u'\xa0', '')
            item['text'] = text
            item['subhead']  = ''
            text_body = sel.xpath("//div[@id='endText']").extract_first()
            html_body = html.unescape(text_body)
            path_md5 = hashlib.sha1(response.url.encode(encoding="utf-8")).hexdigest()
            pic = []
            for url in item['pic']:
                image_guid = hashlib.sha1(url.encode(encoding="utf-8")).hexdigest()
                pic.append({
                        'image_guid':image_guid,
                        'pic_url':url,
                            })
                if url in html_body:
                    html_body = html_body.replace(url, "%s\%s\%s"%(settings['IMAGES_STORE'],path_md5,image_guid))

            item['pic_path'] = {'pic':pic,
                                'pic_path':path_md5,
                                        }
            item['html_file'] = html_body
            item['url'] = response.url

            yield item