import scrapy
from scrapy.selector import Selector
from cnautonews.items import CnautonewsItem

class cnautonews_Spider(scrapy.Spider):
    name = "cnautonews"

    start_urls = [
            "http://www.cnautonews.com/xw/",
            # "http://www.cnautonews.com/gjqc/",
            # "http://www.cnautonews.com/cyc/",
            # "http://www.cnautonews.com/syqc/",
            # "http://www.cnautonews.com/qclbj/",
            # "http://www.cnautonews.com/jxs/",
            # "http://www.cnautonews.com/qchl/",
            # "http://www.cnautonews.com/xnyqc/",
            # "http://www.cnautonews.com/zcfg/",
                ]

    def parse(self, response):
        request = scrapy.Request(url=response.url, callback=self.parse_post, dont_filter=True)
        request.meta['PhantomJS'] = True
        yield request

    def parse_post(self, response):
        sel = Selector(response)
        page_x = sel.xpath("//div[@id='pagenum']/table/tbody/tr/td/table/tbody/tr/td/a/@href").extract()[-1]
        max_page = page_x.split('_')[-1].split('.')[0]  
        from scrapy.shell import inspect_response
        inspect_response(response, self)
        for i in range(int(max_page)+1):
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


    def parse_items(self, response):

        item = CnautonewsItem()
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
        item['pic'] = sel.xpath("//div[@id='document']//img/@src").extract()
        item['summary'] = ''
        info = sel.xpath("//div[@id='document']/div/p/text()").extract()
        text = ''
        for i in info:
            text += i
        item['text'] = text
        item['subhead'] = ''

        yield item