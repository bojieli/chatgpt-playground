import scrapy
import re

domain = 'ustc.edu.cn'
mysql_db = 'spider_ustc'
mysql_host = 'localhost'
mysql_table = 'webpages'

def save_webpage(response):
    print(response.url)
    return

class USTCSpider(scrapy.Spider):
    name = 'ustc-spider'
    start_urls = ['https://' + domain + '/']

    def parse(self, response):
        if 'Content-Type' not in response.headers:
            return
        if not response.headers['Content-Type'].startswith(b'text/'):
            return
        save_webpage(response)

        for next_page in response.css('a::attr(href)'):
            if re.match('https?://([a-z0-9.-]+\.)?' + domain + '/', next_page.get()):
                yield response.follow(next_page, self.parse)
