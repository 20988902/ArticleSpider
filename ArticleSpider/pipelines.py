# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import pymysql
import pymysql.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')    # codes包最大的好处在于打开文件时的编码
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False)+"\n"    # ensure_ascii=False 防止写入中文时出错
        self.file.write(lines)
        return item
    def spider_closed(self, spider):   # 信号量,当爬虫关闭时
        self.file.close()

class MysqlPipeline(object):
    '''
    保存到数据库
    '''
    def __init__(self):
        # 连接数据库
        self.conn = pymysql.connect(
            host='192.168.88.131',
            port=3306,
            user='root',
            passwd='123456',
            db='article_spider',
            charset='utf8'
        )
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article(title, url, create_date, fav_nums) VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item['title'],item['url'],item['create_date'],item['fav_nums']))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
    # 异步插入数据库
    @classmethod
    def from_settings(cls, settings):
        # 读取settings.py
        dbparms = dict(host = settings["MYSQL_HOST"],
            db = 'article_spider',
            user = 'root',
            passwd = '123456',
            charset='utf8',
            cursorclass = pymysql.cursors.DictCursor,)

        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)    # 异常操作异常处理

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入操作
        insert_sql = """
            insert into article(title, url, create_date, fav_nums) VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (item['title'],item['url'],item['create_date'],item['fav_nums']))



class JsonExporterPipeline(object):
    '''
    利用scrapy自带的json写入方式
    '''
    def __init__(self):
        self.file = open('article_export.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
    def close_spider(self, spider):   # 信号量,当爬虫关闭时
        self.exporter.finish_exporting()
        self.file.close()
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            # 获取文件存储路径
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path   # 将数据填充到item

        return item



