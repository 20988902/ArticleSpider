# -*- coding: utf-8 -*-
import re
import datetime

import scrapy
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils import common


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取本页的所有链接，并解析
        2. 获取下一页的url,并下载解析
        """
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")   # 获取图片链接
            post_url = post_node.css("::attr(href)").extract_first("")   # 获取页面url
            obj = Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url":image_url}, callback=self.parse_detail)   # meta传递额外参数给Response
            yield obj   # 交给scrapy下载,执行回调函数

        # 提取下一页url,并交给Scrapy下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            Request(url=next_url, callback=self.parse)


    def parse_detail(self, response):
        # article_item = JobBoleArticleItem()   # 实例化items

        # 提取文章的具体字段
        # front_image_url = response.meta.get("front_image_url", "")   # 获取由Request添加的额外字段
        # title = response.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/h1/text()').extract_first("")
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first("").replace('·','').strip()
        # prais_nums = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract_first("")
        # fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract_first("")
        # match_re = re.match(r".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first("")
        # comment_re = re.match(r".*?(\d+).*", comment_nums)
        # if comment_re:
        #     comment_nums = int(comment_re.group(1))
        # else:
        #     comment_nums = 0
        # content = response.xpath('//div[@class="entry"]').extract_first("")
        # tags_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tags_list = [ ele for ele in tags_list if not ele.strip().endswith('评论')]
        # tags = ','.join(tags_list)
        #
        # # 将数据填充到item
        # article_item["url_object_id"] = common.get_md5(url=response.url)
        # article_item["title"] = title
        # article_item["url"] = response.url
        # try:
        #     create_date = datetime.datetime.strftime(create_date, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now()
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = (front_image_url,)   # 必须传递可迭代对象
        # article_item["prais_nums"] = prais_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] = tags
        # article_item["content"] = content


        # 通过item loader加载items
        front_image_url = response.meta.get("front_image_url", "")
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_xpath('title', '/html/body/div[1]/div[3]/div[1]/div[1]/h1/text()')   # 通过选择器找到数据后，放入到字段里
        item_loader.add_xpath('create_date', '//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_value('url', response.url)  # 直接获取的数据
        item_loader.add_value('url_object_id', common.get_md5(response.url))  # 直接获取的数据
        item_loader.add_value('front_image_url', (front_image_url,))  # 直接获取的数据
        item_loader.add_xpath('prais_nums', '//span[contains(@class, "vote-post-up")]/h10/text()')
        item_loader.add_xpath('fav_nums', '//span[contains(@class, "bookmark-btn")]/text()')
        item_loader.add_xpath('comment_nums', '//a[@href="#article-comment"]/span/text()')
        item_loader.add_xpath('tags', '//p[@class="entry-meta-hide-on-mobile"]/a/text()')
        item_loader.add_xpath('content', '//div[@class="entry"]')

        article_item = item_loader.load_item()   # 解析，生成item对象

        yield article_item   #传递给pipeline


