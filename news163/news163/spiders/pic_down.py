# -*- coding: utf-8 -*-

import scrapy, re, hashlib, html, json
from scrapy.selector import Selector
from news163.items import News163Item
from scrapy.conf import settings
from urllib.parse import unquote

class pic_Spider(scrapy.Spider):
    name = 'pic_download'

    def start_requests(self):
        url = "http://auto.163.com/17/0925/08/CV5T3NVI0008856R.html"
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        item = {}
        sel = Selector(response)
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

        pic_url = sel.xpath("//div[@id='endText']//img/@src").extract()

        text_body = sel.xpath("//div[@id='endText']").extract_first()
        html_body = html.unescape(text_body)
        item['pic'] = pic_url
        path_md5 = hashlib.sha1(response.url.encode(encoding="utf-8")).hexdigest()
        pic = []
        for url in pic_url:
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
        item['keywords'] = ''
        item['text'] = text.replace(r"\n", ' ').replace(r"\r", ' ')
        item['subhead'] = ''
        item['html_file'] = html_body.replace(r"\n", ' ').replace(r"\r", ' ')
        
        item['url'] = response.url

        yield item


