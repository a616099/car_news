# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, http
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random  
from scrapy.conf import settings 

class CnautonewsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

# class PhantomJSMiddleware(object):
#     @classmethod
#     def process_request(cls, request, spider):

#         if request.meta.has_key('PhantomJS'):
#             dcap = dict(DesiredCapabilities.PHANTOMJS)
#             dcap["phantomjs.page.settings.userAgent"] = (
#             "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36"
#             )

#             driver = webdriver.PhantomJS(executable_path="D:\\work-path\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe",
#                         desired_capabilities=dcap
#                             )
#             driver.get(request.url)
#             content = driver.page_source.encode('utf-8')
#             driver.quit()  
#             return http.HtmlResponse(request.url, encoding='utf-8', body=content, request=request)

# class MyproxiesSpiderMiddleware(object):  
  
#       def __init__(self,ip=''):  
#           self.ip=ip  
         
#       def process_request(self, request, spider):  
#           thisip=random.choice(settings.get('IPPOOL'))  
#           print("this is ip:"+thisip["ipaddr"])  
#           request.meta["proxy"]="http://"+thisip["ipaddr"]  