# -*- coding: utf-8 -*-
import scrapy, re, hashlib, html, json, datetime
from scrapy.selector import Selector
from ifeng import cutword
from scrapy.http import FormRequest
import requests

class ifeng_Spider(scrapy.Spider):
    name = 'ifeng'
    start_urls = [
        "http://auto.ifeng.com",
        ]
        
    def start_requests(self):
        #https://api.auto.ifeng.com/cms/api/amop?page=1&pageCount=1000
        # url = "https://api.auto.ifeng.com/cms/api/amop"
        tem_url = lambda n:"https://api.auto.ifeng.com/cms/api/amop?page=%s&pageCount=20"%n
        
        n = 1
        while 1:
            
            resp = requests.get(tem_url(str(n)))
            ajax_data = resp.json()['data']

            if ajax_data:
                for i in ajax_data:
                    try:
                        url = "http://auto.ifeng.com%s"%(i['url'])
                    except:
                        # i = '0'
                        url = "http://auto.ifeng.com%s"%(ajax_data[i]['url'])
                    if '/zhuanlan/' not in url:
                        yield scrapy.Request(url, callback=self.parse_items)
                n += 1
            else:
                break


    def parse_items(self, response): 
        sel = Selector(response)
        item = {}
        item['news_title'] = sel.xpath("//div[@class='arl-cont']/h3/span/text()").extract_first()
        item['post_time'] = sel.xpath("//span[@id='pubtime_baidu']/text()").extract_first()
        item['source'] = sel.xpath("//span[@id='source_baidu']/a/text()").extract_first()
        item['summary'] = ''
        item['author'] = sel.xpath("//span[@id='author_baidu']/a/text()").extract_first()
        item['subhead'] = ''
        item['url'] = response.url

        text_body =  sel.xpath("//div[@class='arl-c-txt']")
        html_body = html.unescape(text_body.extract_first())
        text = text_body.xpath('string(.)').extract_first().replace(u'xa0', u' ')
        item['text'] = text
        path_md5 = hashlib.sha1(response.url.encode(encoding="utf-8")).hexdigest()
        pic_urls = sel.xpath("//div[@class='arl-c-txt']//img/@src").extract()
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
        item['text_sta'] = cutword.cutword(text)

        keywords = sel.xpath("//div[@class='alst']/a/text()").extract() 
        item['keywords_sta'] = cutword.keywords_sta(keywords, text)  
        item['_id'] = path_md5

        yield item