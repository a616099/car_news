# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from caam_news.items import CaamNewsItem

class caam_Spider(scrapy.Spider):
    name = "caam"
    host_url = "http://www.caam.org.cn"
    start_urls = [
        "http://www.caam.org.cn/newslist/a1-1.html",
        "http://www.caam.org.cn/newslist/a2-1.html",
        "http://www.caam.org.cn/newslist/a3-1.html",
        "http://www.caam.org.cn/newslist/a9-1.html",
        "http://www.caam.org.cn/newslist/a5-1.html",
        "http://www.caam.org.cn/newslist/a6-1.html",
        "http://www.caam.org.cn/newslist/a18-1.html",
        ]

    def parse(self, response):
        sel = Selector(response)
        page_x = sel.xpath("/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/div/a")[-1]
        max_numb_t = page_x.xpath("@href").extract_first()
        # u'/newslist/a1-842.html'
        base_url = max_numb_t.split('-')[0]
        max_numb = max_numb_t.split('-')[1].split('.')[0]

        for n in range(int(max_numb)):
            urls = "%s%s-%s.html"%(self.host_url, base_url, str(n+1))
            yield scrapy.Request(urls, callback=self.parse_list_url)

    def parse_list_url(self, response):
        sel = Selector(response)
        list_urls = sel.xpath("//div[@class='xwzxlist xwzxlist_noline']/ul/li/a/@href").extract()
    
        for url in list_urls:
            if "difangzhengce" in url or "guojiazhengce" in url:
                yield scrapy.Request("%s%s"%(self.host_url,url), callback=self.parse_zhengce_items)

            else:
                yield scrapy.Request("%s%s"%(self.host_url,url), callback=self.parse_items)


    def parse_items(self, response):

        item = CaamNewsItem()
        sel = Selector(response)
        newstext = sel.xpath("//div[@class='newstext']")
        item['news_title'] = newstext.xpath("h3/span/text()").extract_first()
        item['post_time'], source = newstext.xpath("div[@class='timecont']/ul/li/text()").extract()
        item["source"] = source[3:]
        item['keywords'] = ''
        item['summary'] = ''
        item['author'] = ''
        item['pic'] = newstext.xpath("p/img/@src").extract()
        info = sel.xpath("//div[@class='newstext']/p")[0]
        item['text'] = info.xpath('string(.)').extract_first()
        item['subhead'] = ''

        yield item

    def parse_zhengce_items(self, response):
    	
        item = CaamNewsItem()
        sel = Selector(response)
        newstext = sel.xpath("//div[@class='newstext']")
        item['news_title'] = newstext.xpath("h3/span/text()").extract_first()
        text = newstext.xpath("ol/li")
        item['post_time'] = text[0].xpath("text()").extract_first()
        item["source"] = text[4].xpath("text()").extract_first()
        item['keywords'] = ''
        item['summary'] = ''
        item['author'] = item["source"]
        item['pic'] = newstext.xpath("p/img/@src").extract()
        info = sel.xpath("//div[@class='newstext']/p")[0]
        item['text'] = info.xpath('string(.)').extract_first()
        item['subhead'] = ''


        yield item