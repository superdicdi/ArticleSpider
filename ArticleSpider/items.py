# -*- coding: utf-8 -*-
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import re
from datetime import datetime

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader


def remove_tags_comment(value):
    if u"评论" in value:
        return ""
    else:
        return value + "520"


def date_convert(value):
    try:
        publish_time = datetime.strptime(value.strip().split()[0], "%Y/%m/%d")
    except Exception as e:
        publish_time = datetime.now()
    return publish_time


def get_nums(value):
    result = re.match(".*?(\d+).*", value)
    if result:
        value = int(result.group(1))
    else:
        value = 0
    return value

def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    # 自定义ItemLoader
    default_output_processor = TakeFirst()

# 默认先调用input_processor，再调用output_processor
class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    publish_time = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    image_url_path = scrapy.Field()
    zan_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    collect_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        # tags 值为list，会按遍历的顺序调用remove_tags_comment这个函数
        input_processor=MapCompose(remove_tags_comment),
        output_processor=Join(",")
    )
