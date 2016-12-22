# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from instagram.items import InstagramHashtagItem, InstagramPostItem, InstagramPostItem2, InstagramUserItem, InstagramUserItem2


class InstagramPipeline(object):
    def __init__(self):
        '''
        self.f = open('C:\\Users\\zachc\\Desktop\\instagram\\instagram\\spiders\\secret.txt', 'r')
        self.secret = self.f.read().split(',')
        self.connection = psycopg2.connect(self.secret[0])
        self.cursor = self.connection.cursor()
        self.log = open('log.txt', 'w')
        self.cursor.execute("CREATE TABLE IF NOT EXISTS insta_posts(tag TEXT, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0), entry NUMERIC(30,10))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS insta_users(username TEXT,  code BIGINT, post_count SMALLINT, follower_count INTEGER, follows_count SMALLINT, privacy TEXT, verification TEXT, entry NUMERIC(30,10))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS insta_hashtags(tag TEXT, posts INTEGER, entry_time NUMERIC(30,10), time_to_top INTEGER, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0))")
       
        self.cursor.execute("CREATE TABLE IF NOT EXISTS insta_posts2 (key SERIAL PRIMARY KEY, tag TEXT, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, commentCount INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, ownerUser TEXT, isVideo TEXT, videoViews INTEGER, imageID NUMERIC(30,0), entry NUMERIC(30,10), location TEXT, slug TEXT, userTags SMALLINT, ad BOOLEAN)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS insta_users2 (key SERIAL PRIMARY KEY, username TEXT,  code BIGINT, post_count SMALLINT, follower_count INTEGER, follows_count SMALLINT, privacy BOOLEAN, verification BOOLEAN, entry NUMERIC(30,10), bio TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS insta_hashtags2 (tag TEXT, posts INTEGER, entry_time NUMERIC(30,10), time_to_top INTEGER, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0))")

        self.counter = 0

        print("STARTING")
        '''

    def close_spider(self, spider):
        from instagram.spiders.jsonSpiderMP import Hashtags, Users, Photos
        '''
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        '''
        print("| TAGS LOGGED {} | USERS LOGGED {} | PHOTOS LOGGED {} |".format(Hashtags, Users, Photos))
        print("SHUTTING DOWN!")
        

    def process_item(self, item, spider):
        '''
        self.counter += 1
        print("Recieved")
        try:
            if isinstance(item, InstagramHashtagItem):
                self.cursor.execute('INSERT INTO insta_hashtags (tag, posts, entry_time, time_to_top, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (item["tag"], item["posts"], item["entry_time"], item["time_to_top"], item["code"], item["date"], item["width"], item["height"], item["comment_count"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["imageID"]))
            elif isinstance(item, InstagramPostItem):
                self.cursor.execute('INSERT INTO insta_posts (tag, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
                    (item["tag"], item["code"], item["date"], item["width"], item["height"], item["comment_count"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["imageID"], item["entry"]))
            elif isinstance(item, InstagramUserItem):
                self.cursor.execute('INSERT INTO insta_users (username, code, post_count, follower_count, follows_count, privacy, verification, entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                    (item["username"], item["code"], item["post_count"], item["follower_count"], item["follows_count"], item["privacy"], item["verification"], item["entry"]))
            elif isinstance(item, InstagramPostItem2):
                self.cursor.execute('INSERT INTO insta_posts2 (tag, code, date, width, height, commentCount, caption, likes, ownerID, isVideo, imageID, entry, location, slug, userTags, ad, videoViews) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
                    (item["tag"], item["code"], item["date"], item["width"], item["height"], item["commentCount"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["imageID"], item["entry"], item["location"], item["slug"], item["userTags"], item["ad"], item["videoViews"],))
            elif isinstance(item, InstagramUserItem2):
                print("OKAY")
                self.cursor.execute('INSERT INTO insta_users2 (username, code, post_count, follower_count, follows_count, privacy, verification, entry, bio) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (item["username"], item["code"], item["postCount"], item["followerCount"], item["followsCount"], item["privacy"], item["verification"], item["entry"], item["bio"]))
            else:
                print("Unknown class")
        except Exception as e:
            print("Error")
            print(e)

        if self.counter % 10 == 0:
            self.connection.commit()

        return item
        '''
        