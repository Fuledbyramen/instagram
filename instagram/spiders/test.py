import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
from time import time
import psycopg2

'''
f = open('secret.txt', 'r')
log = open('log.txt', 'w')
secret = f.read().split(',')

connection = psycopg2.connect(secret[0])
cursor = connection.cursor()

class InstagramSpider(scrapy.Spider):
    name = 'test'

    cursor.execute("CREATE TABLE IF NOT EXISTS insta_posts(tag TEXT, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0), entry NUMERIC(30,10))")
    cursor.execute("CREATE TABLE IF NOT EXISTS insta_users(username TEXT,  code BIGINT, post_count SMALLINT, follower_count INTEGER, follows_count SMALLINT, privacy TEXT, verification TEXT, entry NUMERIC(30,10))")
    cursor.execute("CREATE TABLE IF NOT EXISTS insta_hashtags(tag TEXT, posts INTEGER, entry_time NUMERIC(30,10), time_to_top INTEGER, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0))")

    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = ['https://www.instagram.com']

    def parse(self, response):
        html = str((response.xpath("//body")).extract())
        csrf = re.search(r"csrftoken\=(.+?)\;", str(response.headers)).group(1)
        url = "https://www.instagram.com/instagram/"
        print(html)
        yield Request(url, callback=self.parseUser)

    def parseUser(self, response):
        html = str(response.xpath("//body").extract())

        img_num = str(48)
        code = int(re.search(r"owner\"(?:.+?)([0-9]+)", html).group(1))
        end_cursor = str(re.search(r"end_cursor\"\: \"([0-9]+)", html).group(1))
        url = "https://www.instagram.com/query/?q=ig_user(" + str(code) + ")%20{%20media.after(" + end_cursor + "%2C%20" + img_num + ")%20{%0A%20%20count%2C%0A%20%20nodes%20{%0A%20%20%20%20caption%2C%0A%20%20%20%20code%2C%0A%20%20%20%20comments%20{%0A%20%20%20%20%20%20count%0A%20%20%20%20}%2C%0A%20%20%20%20date%2C%0A%20%20%20%20dimensions%20{%0A%20%20%20%20%20%20height%2C%0A%20%20%20%20%20%20width%0A%20%20%20%20}%2C%0A%20%20%20%20id%2C%0A%20%20%20%20is_video%2C%0A%20%20%20%20likes%20{%0A%20%20%20%20%20%20count%0A%20%20%20%20}%2C%0A%20%20%20%20owner%20{%0A%20%20%20%20%20%20id%0A%20%20%20%20}%2C%0A%20%20%20%20video_views%0A%20%20}%2C%0A%20%20page_info%0A}%0A%20}"      
        yield Request(url, callback=self.parseExtendedUser)

    def parseExtendedUser(self, response):
        html = str(response.xpath("//body").extract())
        print(html)
        cursor.close()
        conn.close()

'''