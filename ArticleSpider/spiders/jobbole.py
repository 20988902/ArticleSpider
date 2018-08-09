# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取本页的所有链接，并解析
        2. 获取下一页的url,并下载解析
        """
        post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()   # 获取href属性的值
        for post_url in post_urls:
            obj = Request(url=post_url, callback=self.parse_detail)
            yield obj   # 交给scrapy下载,执行回调函数

        # 提取下一页url,并交给Scrapy下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            Request(url=next_url, callback=self.parse)


    def parse_detail(self, response):
        # 提取文章的具体字段
        title = response.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/h1/text()').extract_first("")
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first("").replace('·','').strip()
        prais_nums = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract_first("")
        fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract_first("")
        match_re = re.match(r".*?(\d+).*", fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0
        comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first("")
        comment_re = re.match(r".*?(\d+).*", comment_nums)
        if comment_re:
            comment_nums = int(comment_re.group(1))
        else:
            comment_nums = 0
        content = response.xpath('//div[@class="entry"]').extract_first("")
        tags_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tags_list = [ ele for ele in tags_list if not ele.strip().endswith('评论')]
        tags = ','.join(tags_list)




