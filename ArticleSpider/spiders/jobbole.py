# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
import re
import urlparse

from scrapy import Request

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # 解析列表中所有文章 url 并交给 scrapy 下载后进行解析
        post_nodes = response.xpath("//div[@class='post floated-thumb']/div[1]/a")
        for post_node in post_nodes:
            post_url = post_node.xpath("@href").extract_first()
            image_url = post_node.xpath("img/@src").extract_first()
            yield Request(url=urlparse.urljoin(response.url, post_url), callback=self.parse_detail,
                          meta={"image_url": urlparse.urljoin(response.url, image_url)})

        # 提取下一页并交给scrapy进行下载
        next_url = response.xpath("//a[@class ='next page-numbers']/@href").extract_first()
        if next_url:
            yield Request(url=urlparse.urljoin(response.url, next_url), callback=self.parse)

    # def parse_detail(self, response):
    #     # 提取文章具体字段
    #     article = JobBoleArticleItem()
    #     image_url = response.meta.get("image_url", "")  # 文章封面图
    #     title = response.xpath("//h1/text()").extract_first()  # 文章标题
    #     publish_time = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract_first().strip().split()[
    #         0]  # 文章发布时间
    #     zan_nums = int(
    #         response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract_first(default=0))  # 文章点赞数
    #     collect_nums = response.xpath("//span[@data-site-id='2']/text()").extract_first()  # 文章收藏数
    #     result = re.match(".*?(\d+).*", collect_nums)
    #     if result:
    #         collect_nums = int(result.group(1))
    #     else:
    #         collect_nums = 0
    #     comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract_first()  # 文章评论数
    #     result = re.match(".*?(\d+).*", comment_nums)
    #     if result:
    #         comment_nums = int(result.group(1))
    #     else:
    #         comment_nums = 0
    #     content = response.xpath("//div[@class='entry']").extract_first()  # 文章正文内容
    #     tag = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()  # 文章类别
    #     tag = [element for element in tag if not element.strip().endswith(u"评论")]
    #     tags = ",".join(tag)
    #
    #     article["title"] = title
    #     try:
    #         publish_time = datetime.strptime(publish_time, "%Y/%m/%d")
    #     except Exception as e:
    #         publish_time = datetime.now()
    #     article["publish_time"] = publish_time
    #     article["url"] = response.url
    #     article["url_object_id"] = get_md5(response.url)
    #     article["image_url"] = [image_url]
    #     article["zan_nums"] = zan_nums
    #     article["collect_nums"] = collect_nums
    #     article["comment_nums"] = comment_nums
    #     article["content"] = content
    #     article["tags"] = tags
    #
    #     yield article

    def parse_detail(self, response):
        image_url = response.meta.get("image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_xpath("title", "//h1/text()")
        item_loader.add_xpath("publish_time", "//p[@class='entry-meta-hide-on-mobile']/text()")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("image_url", [image_url])
        item_loader.add_xpath("zan_nums", "//span[contains(@class,'vote-post-up')]/h10/text()")
        item_loader.add_xpath("collect_nums", "//span[@data-site-id='2']/text()")
        item_loader.add_xpath("comment_nums", "//a[@href='#article-comment']/span/text()")
        item_loader.add_xpath("content", "//div[@class='entry']")
        item_loader.add_xpath("tags", "//p[@class='entry-meta-hide-on-mobile']/a/text()")

        article = item_loader.load_item()
        yield article