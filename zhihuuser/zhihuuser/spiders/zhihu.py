# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider,Request


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']

    def start_requests(self):
        url=''
        yield Request(url,callback=self.parse())
    def parse(self, response):
        pass
