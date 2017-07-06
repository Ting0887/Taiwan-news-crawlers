#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
東森時報
"""
import scrapy
from scrapy.selector import Selector
import datetime
import re

TODAY = datetime.date.today().strftime('%Y/%m/%d')
TODAY_URL = datetime.date.today().strftime('%Y-%m-%d')
ROOT_URL = 'http://www.ettoday.net'
OLDEST_DATA_YEAR = 2012


class EttodaySpider(scrapy.Spider):
    name = "ettoday_tag"

    def start_requests(self):
        day = datetime.timedelta(days=1)
        NEWS_DATE_BEGIN = datetime.date(OLDEST_DATA_YEAR, 1, 1)
        TODAY = datetime.date.today()
        current_time = NEWS_DATE_BEGIN
        
        while current_time <= TODAY:
            date_str = current_time.strftime('%Y-%m-%d')
            url = 'http://www.ettoday.net/news/news-list-' + date_str + '-0.htm'
            meta = {'iter_time': 0, 'date_str':current_time.strftime('%Y/%m/%d')}
            yield scrapy.Request(url, callback=self.parse_news_list, meta=meta)
            current_time += day

    def parse_news_list(self, response):
        has_next_page = True
        response.meta['iter_time'] += 1
        current_date_str = response.meta['date_str']
        isFirstIter = response.meta['iter_time'] == 1
        prefix = '.part_list_2' if isFirstIter else ''
        for news_item in response.css(prefix+' h3'):
            url = news_item.css('a::attr(href)').extract_first()
            if ROOT_URL not in url:
                url = ROOT_URL + url
            category = news_item.css('em::text').extract_first()
            date_time = news_item.css('span::text').extract_first()

            if current_date_str not in date_time:
                has_next_page = False
                continue

            response.meta['category'] = category
            yield scrapy.Request(url, callback=self.parse_tag_of_news, meta=response.meta)
        if(has_next_page):
            tFile = datetime.date.today().strftime('%Y%m%d') + '.xml'
            yield scrapy.FormRequest(url="http://www.ettoday.net/show_roll.php",
                                     callback=self.parse_news_list,
                                     meta=response.meta,
                                     formdata={'offset': str(response.meta['iter_time']),
                                               'tPage': '3',
                                               'tFile': tFile,
                                               'tOt': '0',
                                               'tSi': '100'
                                               })

        # get scroll news list
        # yield scrapy.Request(url, callback=self.parse_news_list)

    def parse_tag_of_news(self, response):
        print('here')
        tag_string = response.css('head meta[name=news_keywords]::attr(content)').extract_first()
        tags = tag_string.split(',')
        yield {
            'tag': tags
        }