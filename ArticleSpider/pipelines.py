# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import re
import shutil

from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
import pymysql
from scrapy.utils.project import get_project_settings
from twisted.enterprise import adbapi
import scrapy

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="article_spider",
                                    charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole(title, publish_time, url, url_object_id, zan_nums)
            values(%s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql,
                            (item["title"], item["publish_time"], item["url"], item["url_object_id"], item["zan_nums"]))
        self.conn.commit()
        return item


class MysqlTwistedPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        host = settings["MYSQL_HOST"]
        user = settings["USERNAME"]
        password = settings["PASSWORD"]
        database = settings["DATABASE"]
        dbpool = adbapi.ConnectionPool("pymysql", db=database, user=user, passwd=password, host=host,
                                       use_unicode=True, charset='utf8')
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted 将mysql插入变成异步操作
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理一部插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """
                  insert into jobbole(title, publish_time, url, url_object_id, image_url,image_url_path, zan_nums, collect_nums, comment_nums, tags)
                  values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              """
        cursor.execute(insert_sql, (
        item["title"], item["publish_time"], item["url"], item["url_object_id"], item["image_url"],
        item["image_url_path"], item["zan_nums"], item["collect_nums"], item["comment_nums"], item["tags"]))


class ArticleImagePipeline(ImagesPipeline):
    # 从项目设置文件中导入图片下载路径
    img_store = "images"

    # 重写ImagesPipeline类的此方法
    # 发送图片下载请求
    # def get_media_requests(self, item, info):
    #     image_url = item['image_url'] # 如果是集合需要遍历
    #     yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        # for ok, value in results:
        #     item["image_url_path"] = value["path"]
        image_path = [value["path"] for ok, value in results if ok]
        # 定义分类保存的路径
        try:
            local_path = re.match(".*(\.com/|\.cn/)(.*)/((.*)(\.jpg|\.png))$", item['image_url'][0])
            img_path = "%s/%s" % (self.img_store, local_path.group(2))
            # 目录不存在则创建目录
            if os.path.exists(img_path) == False:
                os.makedirs(img_path)
            # 将文件从默认下路路径移动到指定路径下
            shutil.move(self.img_store + "/" + image_path[0], img_path + "/" + local_path.group(3))
            item["image_url_path"] = img_path + "/" + local_path.group(3)
        except Exception as e:
            print(item['image_url'][0])
            print(e)
        return item
