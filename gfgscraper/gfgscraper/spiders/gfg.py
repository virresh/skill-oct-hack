# -*- coding: utf-8 -*-
import scrapy
import boto3
import sys
from decimal import Decimal

num_ques_crawled = 0
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('gfg_questions')


class GfgSpider(scrapy.Spider):
    name = 'gfg'
    allowed_domains = ['www.geeksforgeeks.org']
    custom_settings = {
        'DEPTH_PRIORITY' : 1,
        'SCHEDULER_DISK_QUEUE' : 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE' : 'scrapy.squeues.FifoMemoryQueue',
    }

    start_urls = [
        'https://www.geeksforgeeks.org/data-structures/'
    ]

    def parse(self, response):
        global num_ques_crawled
        if num_ques_crawled >= 500:
            # sys.exit(0)
            return
        # if response.
        is_askable = response.css('div#practiceLinkDiv a::attr(href)')
        if is_askable:
            num_ques_crawled += 1
            # self.log(str(is_askable.extract_first()) + ' ' + response.url)
            text = ''
            for tag in response.css('div.entry-content > *'):
                # print(tag)
                # self.log(tag.xpath('string()'))
                if tag.xpath('@id').extract_first()=='practiceLinkDiv':
                    break
                # print(tag.extract())
                q = tag.xpath('string()').extract_first()
                text += q + '\n'
                # if 'Recommended' in q:
                #     print(tag.xpath('@id').extract_first())
                #     break
                # text += tag.xpath('string(//*)')
            # print(text)
            # print('--@@@@@@============2@@@')
            self.db_pass(response, text)
        elif num_ques_crawled <1:
            for link in response.css('div.entry-content li a::attr(href)'):
                yield scrapy.Request(response.urljoin(link.extract()), callback=self.parse)

            for link in response.css('div#recommendedPostsDiv li a::attr(href)'):
                yield scrapy.Request(response.urljoin(link.extract()), callback=self.parse)

    def db_pass(self, response, text):
        orig_link = response.url
        practice_link = response.css('div#practiceLinkDiv a::attr(href)').extract_first()
        tags = []
        for h in response.css('a[rel~="tag"]::text'):
            tags.append(h.extract())
            # print(h.extract(), response.url)
        title = response.css('h1.entry-title::text').extract_first()
        rating_val = response.css('span#rating_box::text').extract_first()
        text = text.replace('(adsbygoogle = window.adsbygoogle || []).push({});', '')
        dictor = {
            'qlink': orig_link,
            'practice': practice_link,
            'problem': text,
            'title':title,
            'tags': tags,
            'rating': Decimal(rating_val),
        }
        # print(dictor)
        table.put_item(Item=dictor)
