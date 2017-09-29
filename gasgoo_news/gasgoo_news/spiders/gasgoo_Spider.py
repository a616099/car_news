import scrapy
from scrapy.selector import Selector
from gasgoo_news.items import GasgooNewsItem

class gasgoo_Spider(scrapy.Spider):
    name = "gasgoo"
    host_url = "http://auto.gasgoo.com"
    start_urls = [
        "http://auto.gasgoo.com/auto-news/C-101-102-103-104-105-106-501-601"
    ]

    def parse(self, response):
        sel = Selector(response)
        page_x = sel.xpath("//div[@id='ContentPlaceHolder1_pages']/a")
        max_numb = page_x[-3].xpath("text()").extract_first()

        for n in range(int(max_numb)):
            url = "%s/%d"%(response.url, n+1)
            yield scrapy.Request(url, callback=self.parse_list_url)

    def parse_list_url(self, response):
        sel = Selector(response)
        list_urls = sel.xpath("//div[@class='listLeft']/div[@class='content']/h2/a/@href").extract()
        for url in list_urls:
            yield scrapy.Request("%s%s"%(self.host_url,url), callback=self.parse_items)

    def parse_items(self, response):
        item = GasgooNewsItem()
        sel = Selector(response)
        textarea = sel.xpath("//div[@class='listLeft']/div[@class='detailed']")
        item['news_title'] = textarea.xpath("h1/text()").extract_first().strip()
        item['post_time'] = textarea.xpath("div[@class='pageInfo']/span[@class='timeSource']/text()").extract_first()
        item['source'] = textarea.xpath("div[@class='pageInfo']/span/text()").extract()[1:]
        item['keywords'] = textarea.xpath("p[@class='word']/a/text()").extract()
        item['pic'] = textarea.xpath("div[@id='ArticleContent']//img/@src").extract()
        item['summary'] = ''
        item['author'] = ''
        info = textarea.xpath("div[@id='ArticleContent']")[0]
        item['text'] = info.xpath('string(.)').extract_first()
        item['subhead'] = ''
        item['comment'] = '0'
        item['view'] = '0'

        yield item