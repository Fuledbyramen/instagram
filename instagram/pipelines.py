# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from instagram.items import InstagramHashtagItem, InstagramPostItem, InstagramUserItem

class InstagramPipeline(object):
    def __init__(self):
        self.f = open('C:\\Users\\zachc\\Desktop\\instagram\\instagram\\spiders\\secret.txt', 'r')
        self.secret = self.f.read().split(',')
        self.connection = psycopg2.connect(self.secret[0])
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS insta_posts(tag TEXT, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0), entry NUMERIC(30,10))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS insta_users(username TEXT,  code BIGINT, post_count SMALLINT, follower_count INTEGER, follows_count SMALLINT, privacy TEXT, verification TEXT, entry NUMERIC(30,10))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS insta_hashtags(tag TEXT, posts INTEGER, entry_time NUMERIC(30,10), time_to_top INTEGER, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0))")
        self.counter = 0

    def close_spider(self, spider):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        print("SHUTTING DOWN!")

    def process_item(self, item, spider):
        self.counter += 1
        length = len(item)
        
        if isinstance(item, InstagramHashtagItem):
            self.cursor.execute('INSERT INTO insta_hashtags (tag, posts, entry_time, time_to_top, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (item["tag"], item["posts"], item["entry_time"], item["time_to_top"], item["code"], item["date"], item["width"], item["height"], item["comment_count"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["imageID"]))
        elif isinstance(item, InstagramPostItem):
            self.cursor.execute('INSERT INTO insta_posts (tag, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
                (item["tag"], item["code"], item["date"], item["width"], item["height"], item["comment_count"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["imageID"], item["entry"]))
        elif isinstance(item, InstagramUserItem):
            self.cursor.execute('INSERT INTO insta_users (username, code, post_count, follower_count, follows_count, privacy, verification, entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                (item["username"], item["code"], item["post_count"], item["follower_count"], item["follows_count"], item["privacy"], item["verification"], item["entry"]))
        if self.counter % 10 == 0:
            self.connection.commit()

        return item
