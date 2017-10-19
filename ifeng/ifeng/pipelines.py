# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy.conf import settings
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from ifeng import ftp_tool
import scrapy, hashlib, os

class IfengPipeline(object):
 
    collection_name = "ifeng_v2"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].save(dict(item))

class PicDownPlpeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['pic']:
           yield scrapy.Request(image_url,meta={'pic_path':item['pic_path']})

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]

        # 从本地上传到ftp服务器
        if image_paths:
            for dd in image_paths:
                ftp = ftp_tool.ftpconnect(
                        settings['FTP_HOST'],
                        settings['FTP_USER'],
                        settings['FTP_PASSWORD'],
                            )
                ftp_tool.uploadfile(ftp, 
                        settings['FTP_DIR']+dd, 
                        settings['IMAGES_STORE']+dd,
                        )
                #删除本地图片
                folder = settings['IMAGES_STORE']+dd.split('/')[0]
                os.remove(settings['IMAGES_STORE']+dd)
            os.rmdir(folder)

        # if not image_paths:
        #     raise DropItem('图片未下载好 %s'%image_paths)
        return item

    def file_path(self, request, response=None, info=None):

        pic_path = request.meta['pic_path']['pic_path']
        image_guid = hashlib.sha1(request.url.encode(encoding="utf-8")).hexdigest()

        return '%s/%s.jpg' %(pic_path, image_guid)