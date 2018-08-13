# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


def add_jobbole(values):
    return values + "-jobbole"


def date_convert(value):
    try:
        create_date = datetime.datetime.strftime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now()
    return create_date

def get_nums(value):
    comment_re = re.match(r".*?(\d+).*", value)
    if comment_re:
        nums = int(comment_re.group(1))
    else:
        nums = 0
    return nums

def remove_comment_tags(value):
    # 去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value

def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()   # 取数组的第一个数据


class JobBoleArticleItem(scrapy.Item):
    # 定义字段
    title = scrapy.Field(
        input_processor = MapCompose(add_jobbole)   # 对title取到的实际数据，传递给函数处理
    )
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert),
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value),
    )
    front_image_path = scrapy.Field()
    prais_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    tags = scrapy.Field(
        input_processor = MapCompose(remove_comment_tags),
        output_processor = Join(','),   # 使用逗号，连接列表
    )
    content = scrapy.Field()


