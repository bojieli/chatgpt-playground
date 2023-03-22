import scrapy
import re
import pymysql
import datetime    
from scrapy.exceptions import IgnoreRequest
import logging

domain = 'ustc.edu.cn'

mysql_db = 'spider_ustc'
mysql_host = 'localhost'
mysql_user = 'spider'
mysql_password = 'chatgpt-ustc-spider'
mysql_table = 'webpages'

db_conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_db, cursorclass=pymysql.cursors.DictCursor)
if not db_conn:
    print('database connection failed')


def save_webpage(response, utf8_body):
    with db_conn.cursor() as cursor:
        curr_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO " + mysql_table + " (url, data, content_type, crawl_time) VALUES (%s, %s, %s, %s)"
        try:
            content_type_header = response.headers.get('content-type', None)
            cursor.execute(sql, (response.url, utf8_body, content_type_header, curr_time))
            db_conn.commit()
        except Exception as e:
            print('Failed to save to database: ' + str(e))
        return {'url': response.url, 'time': curr_time }
    return None


def should_crawl(url):
    # check whether the URL is in a subdomain of the target website
    if not re.match('https?://([a-z0-9.-]+\.)?' + domain + '/', url):
        return False
    if re.match('https?://mirrors.ustc.edu.cn/', url):
        return False
    if re.match('https?://git.lug.ustc.edu.cn/', url):
        return False
    if re.match('https?://.*.lib.ustc.edu.cn/', url):
        return False
    # avoid URLs that are too long
    if len(url) > 512:
        return False
    # check whether it is an image
    if url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.png') or url.endswith('.gif'):
        return False
    # check whether the URL has been crawled
    with db_conn.cursor() as cursor:
        sql = "SELECT crawl_time FROM " + mysql_table + " WHERE url = %s"
        cursor.execute(sql, (url,))
        if cursor.fetchone():
            return False
    return True


class FilterResponses(object):
    @staticmethod
    def is_valid_response(type_whitelist, content_type_header):
        for type_regex in type_whitelist:
            if re.search(type_regex, content_type_header):
                return True
        return False

    def process_response(self, request, response, spider):
        #type_whitelist = (r'text/', r'application/pdf', r'application/msword', r'officedocument', r'application/vnd.ms-powerpoint', r'openxmlformats')
        type_whitelist = (r'text/', )
        content_type_header = response.headers.get('content-type', None)
        if not content_type_header:
            return response
        content_type_header = content_type_header.decode()
        if self.is_valid_response(type_whitelist, content_type_header):
            return response
        else:
            msg = "Ignoring request {}, content-type {} was not in whitelist".format(response.url, content_type_header)
            logging.log(logging.INFO, msg)
            raise IgnoreRequest()


class USTCSpider(scrapy.Spider):
    name = 'ustc-spider'
    start_urls = ['https://' + domain + '/']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'spider.FilterResponses': 999,
        },
        'DOWNLOAD_MAXSIZE': 8 * 1024 * 1024,
        'DOWNLOAD_TIMEOUT': 10,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,
        'CONCURRENT_REQUESTS': 32,
        'DEPTH_PRIORITY': 1,
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue'
    }

    def parse(self, response):
        content_type = response.headers.get('content-type', None)
        if content_type:
            content_type = content_type.decode().lower()
        if 'gb2312' in content_type:
            utf8_body = response.body.decode('gb2312').encode('utf-8')
        elif 'gbk' in content_type:
            utf8_body = response.body.decode('gbk').encode('utf-8')
        else:
            utf8_body = response.body

        yield save_webpage(response, utf8_body)

        if content_type.startswith('text/'):
            for next_page in response.css('a::attr(href)'):
                absolute_url = response.urljoin(next_page.get())
                if should_crawl(absolute_url):
                    yield response.follow(next_page, callback=self.parse)
