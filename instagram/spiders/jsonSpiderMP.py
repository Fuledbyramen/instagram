import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
from time import time
import psycopg2
import json
try:
    from instagram.items import InstagramHashtagItem, InstagramPostItem, InstagramPostItem2, InstagramUserItem, InstagramUserItem2
except ImportError:
    pass

#| TAGS LOGGED 17 | USERS LOGGED 1357 | PHOTOS LOGGED 15176 | 22 MINUTES
# Ratios - 1.3 minutes per tag
# 79 Users Per Tag
# 892 Photos Per Tag
# 689 Photos Per Minute

#| TAGS LOGGED 22 | USERS LOGGED 1872 | PHOTOS LOGGED 20026 |
#| TAGS LOGGED 22 | USERS LOGGED 1840 | PHOTOS LOGGED 18582 |
#| TAGS LOGGED 19 | USERS LOGGED 1916 | PHOTOS LOGGED 19525 |
#| TAGS LOGGED 21 | USERS LOGGED 1559 | PHOTOS LOGGED 17139 |
#| TAGS LOGGED 22 | USERS LOGGED 1778 | PHOTOS LOGGED 19010 |


#Have to make it smarter
#Regex can rmove all names and captions and bios that bug it out
#Using a dynamic regex with keys()


#if __name__ == "__main__":
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


def validPhoto(item):
    valid = True
    if type(item["tag"]) != str or type(item["code"]) != str or  \
        type(item["caption"]) != str or type(item["ownerUser"]) != str or \
        type(item["isVideo"]) != str or type(item["location"]) != str or \
        type(item["slug"]) != str:
        valid = False
    elif type(item["ad"]) != bool:
        valid = False
    elif item["width"] > 32767 or item["height"] > 32767 or \
        item["userTags"] > 32767:
        valid = False
    elif item["date"] > 2147483647 or item["commentCount"] > 2147483647 or \
        item["likes"] > 2147483647 or item["videoViews"] > 2147483647:
        valid = False
    elif item["ownerID"] > 9223372036854775807:
        valid = False
    elif item["imageID"] > 999999999999999999999999999999 or item["entry"] > 999999999999999999999999999999:
        valid = False

    return valid


def validUser(item):
    if type(item["username"]) != str or  type(item["bio"]) != str:
        return False
    elif type(item["privacy"]) != bool or type(item["verification"]) != bool:
        return False
    elif item["postCount"] > 32767 or item["followsCount"] > 32767:
        return False
    elif item["followerCount"] > 2147483647:
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
    item["ownerID"] = int(j["owner"]["id"])
    item["ownerUser"] = j["owner"]["username"]
    ownerUser = j["owner"]["username"]
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
    if validPhoto(item):
        cursor.execute('INSERT INTO insta_posts4 (tag, code, date, width, height, commentCount, caption, likes, ownerID, ownerUser, isVideo, videoViews, imageID, entry, location, slug, userTags, ad) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
            (item["tag"], item["code"], item["date"], item["width"], item["height"], item["commentCount"], item["caption"], item["likes"], item["ownerID"], "testUsername", item["isVideo"], item["videoViews"], item["imageID"], item["entry"], item["location"], item["slug"], item["userTags"], item["ad"],))    
        Photos += 1
    else:
        log.write(str(item["tag"]) + " " + str(item["code"]) + " " + str(item["date"]) + " " + str(item["width"]) + " " + str(item["height"]) + " " + str(item["commentCount"]) + " " + str(item["caption"]) + " " + str(item["likes"]) + " " + str(item["ownerID"]) + " " + str(item["ownerUser"]) + " " + str(item["isVideo"]) + " " + str(item["videoViews"]) + " " + str(item["imageID"]) + " " + str(item["entry"]) + " " + str(item["location"]) + " " + str(item["slug"]) + " " + str(item["userTags"]) + " " + str(item["ad"]))
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
    item["ownerID"] = int(j["owner"]["id"])
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
    if validPhoto:
        cursor.execute('INSERT INTO insta_posts4 (tag, code, date, width, height, commentCount, caption, likes, ownerID, isVideo, videoViews, imageID, entry, location, slug, userTags, ad) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
            (item["tag"], item["code"], item["date"], item["width"], item["height"], item["commentCount"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["videoViews"], item["imageID"], item["entry"], item["location"], item["slug"], item["userTags"], item["ad"],))    
        Photos += 1
    else:
        log.write(str(item["tag"]) + " " + str(item["code"]) + " " + str(item["date"]) + " " + str(item["width"]) + " " + str(item["height"]) + " " + str(item["commentCount"]) + " " + str(item["caption"]) + " " + str(item["likes"]) + " " + str(item["ownerID"]) + " " + str(item["isVideo"]) + " " + str(item["videoViews"]) + " " + str(item["imageID"]) + " " + str(item["entry"]) + " " + str(item["location"]) + " " + str(item["slug"]) + " " + str(item["userTags"]) + " " + str(item["ad"]))
    #yield item


def logHashtag(json):
    global Hashtags
    item = InstagramHashtagItem()
    j = json["entry_data"]["TagPage"][0]["tag"]
    valid = True
    item["tag"] = j["name"]
    item["posts"] = j["media"]["count"]
    item["entry_time"] = time()
    try:
        item["time_to_top"] = time() - j["top_posts"]["nodes"][0]["date"]
        item["code"] = j["top_posts"]["nodes"][0]["code"]
        item["date"] = j["top_posts"]["nodes"][0]["date"]
        item["width"] = j["top_posts"]["nodes"][0]["dimensions"]["width"]
        item["height"] = j["top_posts"]["nodes"][0]["dimensions"]["height"]
        item["comment_count"] = j["top_posts"]["nodes"][0]["comments"]["count"]
        item["caption"] = j["top_posts"]["nodes"][0]["caption"]
        item["likes"] = j["top_posts"]["nodes"][0]["likes"]["count"]
        item["ownerID"] = int(j["top_posts"]["nodes"][0]["owner"]["id"])
        item["isVideo"] = str(j["top_posts"]["nodes"][0]["is_video"])
        item["imageID"] = int(j["top_posts"]["nodes"][0]["id"])
    except IndexError:
        valid = False
    if valid:
        if validTag(item):
            Hashtags += 1
            cursor.execute('INSERT INTO insta_hashtags2 (tag, posts, entry_time, time_to_top, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (item["tag"], item["posts"], item["entry_time"], item["time_to_top"], item["code"], item["date"], item["width"], item["height"], item["comment_count"], item["caption"], item["likes"], item["ownerID"], item["isVideo"], item["imageID"]))    
        else:
            log.write(str(item["tag"]) + " " + str(item["posts"]) + " " + str(item["entry_time"]) + " " + str(item["time_to_top"]) + " " + str(item["code"]) + " " + str(item["date"]) + " " + str(item["width"]) + " " + str(item["height"]) + " " + str(item["comment_count"]) + " " + str(item["caption"]) + " " + str(item["likes"]) + " " + str(item["ownerID"]) + " " + str(item["isVideo"]) + " " + str(item["imageID"]))
        connection.commit()
        #yield item


def logUser(json):
    global Users
    item = InstagramUserItem2()
    user = json["entry_data"]["ProfilePage"][0]["user"]
    item["username"] = user["username"]
    item["code"] = int(user["id"])
    item["postCount"] = user["media"]["count"]
    item["followerCount"] = user["followed_by"]["count"]
    item["followsCount"] = user["follows"]["count"]
    item["privacy"] = user["is_private"]
    item["verification"] = user["is_verified"]
    item["bio"] = user["biography"]
    item["entry"] = time()
    if validUser(item):
        Users += 1
        cursor.execute('INSERT INTO insta_users2 (username, code, post_count, follower_count, follows_count, privacy, verification, entry, bio) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (item["username"], item["code"], item["postCount"], item["followerCount"], item["followsCount"], item["privacy"], item["verification"], item["entry"], item["bio"]))
        connection.commit()
        
    else:
        log.write(str(item["username"]) + " " + str(item["code"]) + " " + str(item["postCount"]) + " " + str(item["followerCount"]) + " " + str(item["followsCount"]) + " " + str(item["privacy"]) + " " + str(item["verification"]) + " " + str(item["entry"]) + " " + str(item["bio"]))
    #yield item


class InstagramSpider(scrapy.Spider):
    name = 'jsonSpiderMP'
    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = ["https://www.instagram.com/"]

    custom_settings = {"LOG_LEVEL" : 'WARNING'}

    def __init__(self, low, high, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.high = high
        self.low = low


    def parse(self, response):
        print(self.low + " " + self.high)
        #begins spider, needs to go to instagram first
        urls = []
        cursor.execute("SELECT hashtag from hashtags WHERE key > %s AND key < %s" % (self.low, self.high))
        hashtags = cursor.fetchall()
        for tag in hashtags:
            urls.append("https://www.instagram.com/explore/tags/{}/".format(tag[0]))
        for url in urls:
            yield Request(url, callback=self.parseStartHashtag)


    def parseStartHashtag(self, response):
        html = str((response.xpath("//body")).extract())
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("'", '"').replace("\\u2800", "").replace("\\\\\"", "'").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("/", "\/")
        
        try:
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
        except json.decoder.JSONDecodeError as e:
            i = re.search(r"column ([0-9]+)", str(e)).group(1)
            print(string[int(i)-20 : int(i)+20])


    def parsePhoto(self, response):
        html = str((response.xpath("//body")).extract())
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("'", '"').replace("\\u2800", "").replace("\\\\\"", "'").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("/", "\/")
        try:
            j = json.loads(string)
             
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
        except json.decoder.JSONDecodeError as e:
            i = re.search(r"column ([0-9]+)", str(e)).group(1)
            print(string[int(i)-20 : int(i)+20])
        
        
    def parseUser(self, response):
        html = str((response.xpath("//body")).extract())
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("'", '"').replace("\\u2800", "").replace("\\\\\"", "'").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("/", "\/")
        captions = re.findall(r"caption\"\: \"(.+?)\"\, \"\w+\"\: \{", string)
        for caption in captions:
            string = string.replace(caption, "")
        try:
            bio = re.search(r"\"biography\"\: \"(.+?)\"\, \"\w+\"\: ", string).group(1)
            string = string.replace(bio, "")
        except AttributeError:
            pass
        try:
            j = json.loads(string)
            logUser(j)
            for post in j["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]:
                logPhotoPage(post, username=response.meta["username"])
        except json.decoder.JSONDecodeError as e:
            i = re.search(r"column ([0-9]+)", str(e)).group(1)
            print(string[int(i)-20 : int(i)+20])
        










        

