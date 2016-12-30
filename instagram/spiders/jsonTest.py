import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
from time import time
import psycopg2
import json
from instagram.items import InstagramHashtagItem, InstagramPostItem, InstagramPostItem2, InstagramUserItem, InstagramUserItem2


if __name__ == "__main__":
    f = open('secret.txt', 'r')
    log = open('log.txt', 'w')
    secret = f.read().split(',')
    #connection = psycopg2.connect(secret[0])
    #cursor = connection.cursor()


def boolean(string):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        print("Error in boolean function. Neither true nor false.")


def validPhoto(item):
    if type(item["tag"]) != str or type(item["code"]) != str or  \
        type(item["caption"]) != str or type(item["ownerUser"]) != str or \
        type(item["isVideo"]) != str or type(item["location"]) != str or \
        type(item["slug"]) != str:
        return False
    elif type(item["ad"]) != bool:
        return False
    elif item["width"] > 32767 or item["height"] > 32767 or \
        item["userTags"] > 32767:
        return False
    elif item["date"] > 2147483647 or item["commentCount"] > 2147483647 or \
        item["likes"] > 2147483647 or item["videoViews"] > 2147483647:
        return False
    elif item["ownerID"] > 9223372036854775807:
        return False
    elif item["imageID"] > 999999999999999999999999999999 or item["entry"] > 999999999999999999999999999999:
        return False
    return True


def validUser(item):
    if type(item["username"]) != str or type(item["verification"]) != str or  \
        type(item["privacy"]) != str or type(item["bio"]) != str:
        return False
    elif item["post_count"] > 32767 or item["follows_count"] > 32767:
        return False
    elif item["follower_count"] > 2147483647:
        return False
    elif item["code"] > 9223372036854775807:
        return False
    elif item["entry"] > 999999999999999999999999999999:
        return False
    return True


def validTag(item):
    if type(item["tag"]) != str or type(item["code"]) != str or  \
        type(item["isVideo"]) != str or type(item["caption"]) != str:
        return False
    elif item["width"] > 32767 or item["height"] > 32767:
        return False
    elif item["posts"] > 2147483647 or item["time_to_top"] > 2147483647 or \
        item["date"] > 2147483647 or item["comment_count"] > 2147483647 or \
        item["likes"] > 2147483647:
        return False
    elif item["ownerID"] > 9223372036854775807:
        return False
    elif item["entry_time"] > 999999999999999999999999999999 or item["imageID"] > 999999999999999999999999999999:
        return False
    return True


def logPhoto(json, tag="FromUser"):
    for j in json:
        item = InstagramPostItem2()
        item["tag"] = tag
        item["code"] = j["code"]
        item["date"] = j["date"]
        item["width"] = j["dimensions"]["width"]
        item["height"] = j["dimensions"]["height"]
        item["commentCount"] = j["comments"]["count"]
        item["caption"] = j["caption"]
        item["likes"] = j["likes"]["count"]
        item["ownerID"] = j["owner"]["id"]
        item["isVideo"] = j["is_video"]
        item["imageID"] = int(j["id"])
        item["entry"] = time()
        try:
            item["location"] = j["location"]["name"]
            item["slug"] = j["location"]["slug"]
        except TypeError:
            item["location"] = "None"
            item["slug"] = "None"
        try:
            item["userTags"] = len(j["usertags"])
        except TypeError:
            item["userTags"] = 0
        try:
            item["ad"] = j["is_ad"]
        except TypeError:
            item["ad"] = False   
        if validPhoto(item): 
            cursor.execute('INSERT INTO insta_posts2 (tag, code, date, width, height, commentCount, caption, likes, ownerID, isVideo, imageID, entry, location, slug, userTags, ad) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
                (item["tag"], item["code"], item["date"], item["width"], item["height"], item["commentCount"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["imageID"], item["entry"], item["location"], item["slug"], item["userTags"], item["ad"],))    
        else:
            log.write(item)
        #yield item


def logHashtag(json, tag):
    item = InstagramHashtagItem2()
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
    if validTag(item):
        cursor.execute('INSERT INTO insta_hashtags (tag, posts, entry_time, time_to_top, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (item["tag"], item["posts"], item["entry_time"], item["time_to_top"], item["code"], item["date"], item["width"], item["height"], item["comment_count"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["imageID"]))    
    else:
        log.write(item)
    connection.commit()
    #yield item


def logUser(json):
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
    if validUser(item):
        cursor.execute('INSERT INTO insta_users2 (username, code, post_count, follower_count, follows_count, privacy, verification, entry, bio) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (item["username"], item["code"], item["postCount"], item["followerCount"], item["followsCount"], item["privacy"], item["verification"], item["entry"], item["bio"]))
    else:
        log.write(item)
    #yield item


class InstagramSpider(scrapy.Spider):
    name = 'jsonTest'
    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    #start_urls = ["https://www.instagram.com/p/BOQCqAOgqZE/"]
    start_urls = ["https://www.instagram.com/nike/"]
    #start_urls = ["https://www.instagram.com/explore/tags/instagood/"]

    #def __init__(self, name, *args, **kwargs):
        #super(InstagramSpider, self).__init__(*args, **kwargs)
        #self.start_urls = start_urls = ["https://www.instagram.com/{}/".format(name)]

    def parse(self, response):
        html = str((response.xpath("//body")).extract())
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'")
        j = json.loads(string)

        print(j["config"]["viewer"].keys())
        #print(j["entry_data"]["TagPage"][0]["top_posts"]["nodes"][0].keys())
        #print(j["entry_data"]["PostPage"][0]["media"].keys())
        #print(j["entry_data"]["PostPage"][0]["media"]["comments"]["nodes"].keys())

    def parsePhoto(self, response):
        html = str((response.xpath("//body")).extract())
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'")
        j = json.loads(string)
        print(j["entry_data"]["PostPage"][0]["media"]["owner"]["username"])
        print((j["entry_data"]["PostPage"][0]["media"]["comments"]["nodes"][0]["user"]["username"]))
        print(j["entry_data"]["PostPage"][0]["media"]["location"])

        photo = j["entry_data"]["PostPage"][0]["media"]

        code = photo["code"]
        date = photo["date"]
        width = photo["dimensions"]["width"]
        height = photo["dimensions"]["height"]
        comment_count = photo["comments"]["count"]
        caption = photo["caption"]
        likes = photo["likes"]
        ownerID = photo["owner"]["id"]
        ownerUser = photo["owner"]["username"]
        isVideo = photo["is_video"]
        imageID = photo["id"]
        entry = time()
        if isVideo:
            video_views = photo["video_views"]
        else:
            video_views = 0
        try:
            location = photo["location"]["name"]
            slug = photo["location"]["slug"]
        except TypeError:
            location = "None"
            slug = "None"
        user_tags = len(j["entry_data"]["PostPage"][0]["media"]["usertags"]["nodes"])
        ad = photo["is_ad"]

        privacy = photo["owner"]["is_private"]



    def parseUser(self, response):
        html = str((response.xpath("//body")).extract())
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'")
        j = json.loads(string)
        for j in j["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]:
            print(j.keys())
        #print(j["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"][0].keys())
        


