import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
from time import time
import psycopg2
import json
from instagram.items import InstagramHashtagItem, InstagramPostItem, InstagramPostItem2, InstagramUserItem, InstagramUserItem2


f = open('secret.txt', 'r')
log = open('log.txt', 'w')
secret = f.read().split(',')
connection = psycopg2.connect(secret[0])
cursor = connection.cursor()
usedUsers = []
commitCounter = 0

Hashtags = 0
Photos = 0
Users = 0

def boolean(string):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        print("Error in boolean function. Neither true nor false.")

def commit():
    global commitCounter
    commitCounter += 1
    if commitCounter % 25 == 0:
        connection.commit()

#if the photo is taken from a hashtag there is a possibility location, slug and ad will be filled
#if the photo is taken from a user the location slug and is ad will always be null

#logs photo from a direct photo url
def logPhotoDirect(j, tag="FromUser"):
    global Photos
    item = InstagramPostItem2()
    item["tag"] = tag
    item["code"] = j["code"]
    item["date"] = j["date"]
    item["width"] = j["dimensions"]["width"]
    item["height"] = j["dimensions"]["height"]
    item["commentCount"] = j["comments"]["count"]
    try:
        item["caption"] = j["caption"]
    except KeyError:
        item["caption"] = "None"
    item["likes"] = j["likes"]["count"]
    item["ownerID"] = j["owner"]["id"]
    item["ownerUser"] = j["owner"]["username"]
    item["isVideo"] = j["is_video"]
    item["imageID"] = int(j["id"])
    item["entry"] = time()
    if item["isVideo"]:
        item["videoViews"] = j["video_views"]
    else:
        item["videoViews"] = 0
    try:
        item["location"] = j["location"]["name"]
        item["slug"] = j["location"]["slug"]
    except (KeyError, TypeError):
        item["location"] = "None"
        item["slug"] = "None"
    try:
        item["userTags"] = len(j["usertags"])
    except (KeyError, TypeError):
        item["userTags"] = 0
    try:
        item["ad"] = j["is_ad"]
    except (KeyError, TypeError):
        item["ad"] = False    
    cursor.execute('INSERT INTO insta_posts2 (tag, code, date, width, height, commentCount, caption, likes, ownerID, ownerUser, isVideo, videoViews, imageID, entry, location, slug, userTags, ad) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
        (item["tag"], item["code"], item["date"], item["width"], item["height"], item["commentCount"], item["caption"], item["likes"], item["ownerID"], item["ownerUser"], item["isVideo"], item["videoViews"], item["imageID"], item["entry"], item["location"], item["slug"], item["userTags"], item["ad"],))    
    Photos += 1
    #yield item

#logs photos from a page aka a user page or hashtag page
def logPhotoPage(j, username, tag="FromUser"):
    global Photos
    item = InstagramPostItem2()
    item["tag"] = tag
    item["code"] = j["code"]
    item["date"] = j["date"]
    item["width"] = j["dimensions"]["width"]
    item["height"] = j["dimensions"]["height"]
    item["commentCount"] = j["comments"]["count"]
    try:
        item["caption"] = j["caption"]
    except KeyError:
        item["caption"] = "None"
    item["likes"] = j["likes"]["count"]
    item["ownerID"] = j["owner"]["id"]
    item["ownerUser"] = username
    item["isVideo"] = j["is_video"]
    item["imageID"] = int(j["id"])
    item["entry"] = time()
    if item["isVideo"]:
        item["videoViews"] = j["video_views"]
    else:
        item["videoViews"] = 0   
    item["location"] = "None"
    item["slug"] = "None"
    item["userTags"] = 0
    item["ad"] = False
    cursor.execute('INSERT INTO insta_posts2 (tag, code, date, width, height, commentCount, caption, likes, ownerID, isVideo, videoViews, imageID, entry, location, slug, userTags, ad) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
        (item["tag"], item["code"], item["date"], item["width"], item["height"], item["commentCount"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["videoViews"], item["imageID"], item["entry"], item["location"], item["slug"], item["userTags"], item["ad"],))    
    Photos += 1
    #yield item


def logHashtag(json):
    global Hashtags
    item = InstagramHashtagItem()
    j = json["entry_data"]["TagPage"][0]["tag"]
    item["tag"] = j["name"]
    item["posts"] = j["media"]["count"]
    item["entry_time"] = time()
    item["time_to_top"] = time() - j["top_posts"]["nodes"][0]["date"]
    item["code"] = j["top_posts"]["nodes"][0]["code"]
    item["date"] = j["top_posts"]["nodes"][0]["date"]
    item["width"] = j["top_posts"]["nodes"][0]["dimensions"]["width"]
    item["height"] = j["top_posts"]["nodes"][0]["dimensions"]["height"]
    item["comment_count"] = j["top_posts"]["nodes"][0]["comments"]["count"]
    item["caption"] = j["top_posts"]["nodes"][0]["caption"]
    item["likes"] = j["top_posts"]["nodes"][0]["likes"]["count"]
    item["ownerID"] = j["top_posts"]["nodes"][0]["owner"]["id"]
    item["isVideo"] = j["top_posts"]["nodes"][0]["is_video"]
    item["imageID"] = int(j["top_posts"]["nodes"][0]["id"])
    cursor.execute('INSERT INTO insta_hashtags2 (tag, posts, entry_time, time_to_top, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (item["tag"], item["posts"], item["entry_time"], item["time_to_top"], item["code"], item["date"], item["width"], item["height"], item["comment_count"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["imageID"]))    
    Hashtags += 1
    #yield item


def logUser(json):
    global Users
    item = InstagramUserItem2()
    user = json["entry_data"]["ProfilePage"][0]["user"]
    item["username"] = user["username"]
    item["code"] = user["id"]
    item["postCount"] = user["media"]["count"]
    item["followerCount"] = user["followed_by"]["count"]
    item["followsCount"] = user["follows"]["count"]
    item["privacy"] = user["is_private"]
    item["verification"] = user["is_verified"]
    item["bio"] = user["biography"]
    item["entry"] = time()
    cursor.execute('INSERT INTO insta_users2 (username, code, post_count, follower_count, follows_count, privacy, verification, entry, bio) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (item["username"], item["code"], item["postCount"], item["followerCount"], item["followsCount"], item["privacy"], item["verification"], item["entry"], item["bio"]))
    connection.commit()
    Users += 1
    #yield item


class InstagramSpider(scrapy.Spider):
    name = 'jsonSpider'
    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = ["https://www.instagram.com/instagram/"]

    def parse(self, response):
        #begins spider, needs to go to instagram first
        urls = []
        cursor.execute("SELECT hashtag from hashtags WHERE key > 11 AND key < 61")
        hashtags = cursor.fetchall()
        for tag in hashtags:
            urls.append("https://www.instagram.com/explore/tags/{}/".format(tag[0]))
        for url in urls:
            yield Request(url, callback=self.parseStartHashtag)

    def parseStartHashtag(self, response):
        html = str((response.xpath("//body")).extract())
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'")
        j = json.loads(string)

        logHashtag(j)
        tag = j["entry_data"]["TagPage"][0]["tag"]["name"]
        codes = []
        #takes photo codes from top posts
        for i in j["entry_data"]["TagPage"][0]["tag"]["top_posts"]["nodes"]:
            codes.append(i["code"])
        #takes photo codes from media posts
        for i in j["entry_data"]["TagPage"][0]["tag"]["media"]["nodes"]:
            codes.append(i["code"])
        for code in codes:
            url = "https://www.instagram.com/p/{}/".format(code)
            yield Request(url, callback=self.parsePhoto, meta={"tag" : tag})

    def parsePhoto(self, response):
        html = str((response.xpath("//body")).extract())
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'")
        j = json.loads(string)
        jArg = j["entry_data"]["PostPage"][0]["media"]
        logPhotoDirect(jArg, response.meta["tag"])

        usernames = []
        #owner of the photo
        owner = j["entry_data"]["PostPage"][0]["media"]["owner"]["username"]
        if owner not in usedUsers:
            usernames.append(owner)
        #for each comment find the username
        for j in j["entry_data"]["PostPage"][0]["media"]["comments"]["nodes"]:
            tempName = j["user"]["username"]
            #check if this spider instance has already logged user
            if tempName not in usedUsers:
                usedUsers.append(tempName)
                usernames.append(tempName)

        for user in usernames:
            url = "https://www.instagram.com/{}/".format(user)
            yield Request(url, callback=self.parseUser, meta={"username" : user})

    def parseUser(self, response):
        html = str((response.xpath("//body")).extract())
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'")
        j = json.loads(string)
        logUser(j)
        for post in j["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]:
            logPhotoPage(post, username=response.meta["username"])










        

