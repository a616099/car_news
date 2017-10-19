# -*- coding: utf-8 -*-
import scrapy, re, hashlib, html, json, datetime
from scrapy.selector import Selector
from cnautonews.items import CnautonewsItem
from cnautonews import cutword
from scrapy.conf import settings

class cnautonews_Spider(scrapy.Spider):
    name = "cnautonews"

    start_urls = [
            "http://www.cnautonews.com/xw/",
            "http://www.cnautonews.com/gjqc/",
            "http://www.cnautonews.com/cyc/",
            "http://www.cnautonews.com/syqc/",
            "http://www.cnautonews.com/qclbj/",
            "http://www.cnautonews.com/jxs/",
            "http://www.cnautonews.com/qchl/",
            "http://www.cnautonews.com/xnyqc/",
            "http://www.cnautonews.com/zcfg/",
                ]

    # def parse(self, response):
    #     maxpage = re.search(r"var countPage = (\d*)\//", text).group(1)
    #     request = scrapy.Request(url=response.url, callback=self.parse_post, dont_filter=True)
    #     # request.meta['PhantomJS'] = True
    #     yield request

    def parse(self, response):
        sel = Selector(response)
        max_page = re.search(r"var countPage = (\d*)\//", response.text).group(1)
        # page_x = sel.xpath("//div[@id='pagenum']/table/tbody/tr/td/table/tbody/tr/td/a/@href").extract()[-1]
        # max_page = page_x.split('_')[-1].split('.')[0]  
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        for i in range(int(max_page)):
            if i == 0:
                url = response.url
            else:
                #http://www.cnautonews.com/gjqc/index_1.htm
                url = "%sindex_%s.htm"%(response.url, str(i))

            yield scrapy.Request(url, callback=self.parse_list_url )

    def parse_list_url(self, response):

        sel = Selector(response)
        list_urls = sel.xpath("//div[@id='pd']/ul/li/a/@href").extract()
        tem = response.url.split("/index")[0]
 
        #./201708/t20170831_552508.htm
        for i in list_urls:
            url = "%s%s"%(tem, i[1:])
            yield scrapy.Request(url, callback=self.parse_items)

    # def start_requests(self):
    #     url = 'http://www.cnautonews.com/xw/201705/t20170531_538832.htm'
    #     yield scrapy.Request(url, callback=self.parse_items)

    def parse_items(self, response):

        item = {}
        sel = Selector(response)
        item['news_title'] = sel.xpath("//div[@id='dtitle']/text()").extract_first()
        string = sel.xpath("//div[@id='dsource']/text()").extract_first().split(u'\xa0')
        item['post_time'] = string[0]
        item['source'] = string[1]
        try:
            item['author'] = string[2]
        except:
            item['author'] = ''
        item['keywords'] = ''
        item['summary'] = ''
        info = sel.xpath("//div[@id='document']/div/p/text()").extract()
        text = ''
        for i in info:
            text += i
        item['text'] = text
        item['subhead'] = '' 
        pic_urls_temp = sel.xpath("//div[@id='document']//img/@src").extract()
        pic_urls = []
        base_url = '/'.join(response.url.split('/')[:-1])
        for u in pic_urls_temp:
            if u.startswith('.'):
                s = '%s/%s'%(base_url, u.strip('.'))
                pic_urls.append(s)
            else:
                pic_urls.append(u)

        text_body = sel.xpath("//div[@class='TRS_Editor']").extract_first()
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
        item['url'] = response.url
        # item['url_md5'] = path_md5
        item['_id'] = path_md5
        item['text_sta'] = cutword.cutword(text)

        yield item