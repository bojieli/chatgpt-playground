import scrapy
import re
import pymysql
import datetime    

domain = 'ustc.edu.cn'

mysql_db = 'spider_ustc'
mysql_host = 'localhost'
mysql_user = 'spider'
mysql_password = 'chatgpt-ustc-spider'
mysql_table = 'webpages'

db_conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_db, cursorclass=pymysql.cursors.DictCursor)
if not db_conn:
    print('database connection failed')


def save_webpage(response):
    with db_conn.cursor() as cursor:
        curr_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO " + mysql_table + " (url, data, crawl_time) VALUES (%s, %s, %s)"
        try:
            cursor.execute(sql, (response.url, response.body, curr_time))
            db_conn.commit()
        except Exception as e:
            print('Failed to save to database ' + str(e))
        return {'url': response.url, 'time': curr_time }
    return None


def should_crawl(url):
    # check whether the URL is in a subdomain of the target website
    if not re.match('https?://([a-z0-9.-]+\.)?' + domain + '/', url):
        return False
    # check whether the URL has been crawled
    with db_conn.cursor() as cursor:
        sql = "SELECT crawl_time FROM " + mysql_table + " WHERE url = %s"
        cursor.execute(sql, (url,))
        if cursor.fetchone():
            return False
    return True


class USTCSpider(scrapy.Spider):
    name = 'ustc-spider'
    start_urls = ['https://' + domain + '/']

    def parse(self, response):
        if 'Content-Type' not in response.headers:
            return
        content_type = response.headers['Content-Type'].lower()
        if not content_type.startswith(b'text/'):
            return
        if b'gb2312' in content_type:
            response.body = response.body.decode('gb2312').encode('utf-8')
        elif b'gbk' in content_type:
            response.body = response.body.decode('gbk').encode('utf-8')

        yield save_webpage(response)

        for next_page in response.css('a::attr(href)'):
            absolute_url = response.urljoin(next_page.get())
            if should_crawl(absolute_url):
                yield response.follow(next_page, self.parse)
