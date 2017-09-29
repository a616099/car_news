import scrapy
from scrapy.selector import Selector
from ifeng.items import IfengItem
from scrapy.http import FormRequest
import requests

class ifeng_Spider(scrapy.Spider):
    name = 'ifeng'
    start_urls = [
        "http://auto.ifeng.com",
        ]
        
    def parse(self, response):
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
                    yield scrapy.Request(url, callback=self.parse_items)
                n += 1
            else:
                break


    def parse_items(self, response): 
        item = IfengItem()
        sel = Selector(response)
        item['news_title'] = sel.xpath("//div[@class='arl-cont']/h3/span/text()").extract_first()
        item['post_time'] = sel.xpath("//span[@id='pubtime_baidu']/text()").extract_first()
        item['source'] = sel.xpath("//span[@id='source_baidu']/a/text()").extract_first()
        item['keywords'] = ''
        item['summary'] = ''
        item['author'] = ''
        info =  sel.xpath("//div[@class='arl-c-txt']")
        item['pic'] = sel.xpath("//div[@class='arl-c-txt']//img/@src").extract()
        item['text'] = info.xpath('string(.)').extract_first().replace(u'xa0', u' ')
        item['subhead'] = ''
        item['comment'] = sel.xpath("//div[@class='comment-tit']/div/div/text()").extract()[1]
        item['views'] = '0'
        item['url'] = response.url
        yield item