import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
from time import time
import psycopg2
from instagram.items import InstagramHashtagItem, InstagramPostItem, InstagramUserItem

'''
#Take in hashtag names, log top posts,
#users from posts then those users, continue on

f = open('secret.txt', 'r')
log = open('log.txt', 'w')
secret = f.read().split(',')
connection = psycopg2.connect(secret[0])
cursor = connection.cursor()


def boolean(string):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        print("Error in boolean function. Neither true nor false.")


def regexExceptionInt(regex, html):
    try:
        out = int(re.search(r"{}".format(regex), html).group(1))
    except AttributeError:
        out = 0
    return out


def regexExceptionStr(regex, html):
    try:
        out = str(re.search(r"{}".format(regex),html).group(1))
    except AttributeError as e:
        out = "None"
        #print(e)
    return out

def extractPostsFromPage(html, response, tag="FromUser", top_post = False):

    #all image url codes on the page
    if not top_post:
        url_codes = re.findall(r"\"code\"\: \"(.+?)\"", html)
    #used for extracting the top post information specifically if set to true
    #sets the code to be code of top post, a list of one code
    else:
        try:
            url_codes = [re.search(r"top_posts(?:.+?)code\"\: \"(.+?)\"", html).group(1)]
        except AttributeError:
            url_codes = re.findall(r"\"code\"\: \"(.+?)\"", html)

    #matches the code to the regex to ensure all regexes are to exact image
    for code in url_codes:
        try:
            width = int(re.search(r"{}(?:.+?)width\"\: ([0-9]+)".format(code), html).group(1))
            height = int(re.search(r"{}(?:.+?)height\"\: ([0-9]+)".format(code), html).group(1))
            comment_count = int(re.search(r"{}(?:.+?)comments(?:.+?)([0-9]+)".format(code), html).group(1))
            try:
                caption = re.search(r"{}(?:.+?)\"caption\"\: \"(.+?)\",".format(code), html).group(1)
            except AttributeError:
                try:
                    caption = re.search(r"{}(?:.+?)caption\"\: \"(.+?)\"\, \"thumbnail_src".format(code), html).group(1)
                except AttributeError:
                    try:
                        caption = re.search(r"{}(?:.+?)\"caption\"\: \"(.+?)\", \"comments".format(code), html).group(1)
                    except AttributeError:
                        caption = "None"
            likes = int(re.search(r"{}(?:.+?)\"likes\"\: (?:.+?)count\"\: ([0-9]+)".format(code), html).group(1))
            ownerID = int(re.search(r"{}(?:.+?)owner\"\: (?:.+?)id\"\: \"([0-9]+)".format(code), html).group(1))
            isVideo = re.search(r"{}(?:.+?)likes(?:.+?)is_video\"\: ([a-z]+)".format(code), html).group(1)

            
            try:
                date = int(re.search(r"{}(?:.+?)date\"\: ([0-9]+)".format(code), html).group(1))
            except AttributeError:
                date = 0
            imageID = int(re.search(r"{}(?:.+?)likes(?:.+?)owner(?:.+?)is_video(?:.+?)id\"\: \"([0-9]+)".format(code), html).group(1))
            try:
                location = re.search(r"location(?:.+?)\"name\"\: \"(.+?)\"(?:.+?){}".format(code), html).group(1)
            except AttributeError:
                location = "None"
            try:
                slug = re.search(r"slug\"\: \"(.+?)\"(?:.+?){}".format(code), html).group(1)
            except AttributeError:
                slug = "None"
            try:
                user_tags = len(re.findall(r"\"x\"\: ([0-9])(?:.+?)\"y\"(?:.+?){}".format(code), html))
            except AttributeError:
                user_tags = 0 
            try:
                ad = boolean(re.search(r"{}(?:.+?)\"is_ad\"\: ([a-z]+)".format(code), html).group(1))
            except AttributeError:
                ad = False
            entry = time()


            if top_post:
                return code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry
            else:
                if not top_post:
                    #posts are sorted by tags or user id's
                    try:
                        cursor.execute('INSERT INTO insta_posts2 (tag, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry, location, slug, user_tags, ad) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (tag, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry, location, slug, user_tags, ad))
                    except Exception as e:
                        #print (e)
                        pass
        except AttributeError as e:
            print(str(e) + " " + str(code) + " " + response)
    connection.commit()



class InstagramSpider(scrapy.Spider):
    name = '1217spider'
    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = ["https://www.instagram.com"]

    connection.commit()

    log.write("Starting")

    def parse(self, response):
        start_urls = []
        cursor.execute("SELECT hashtag FROM hashtags WHERE key > 20 and key < 30")
        codes = cursor.fetchall()
        for code in codes:
            start_urls.append("https://www.instagram.com/explore/tags/{}/".format(code[0]))
        for url in start_urls:
            yield Request(url, callback=self.parseStartHashtag)


    def parseStartHashtag(self, response):
        html = str((response.xpath("//body")).extract())
        #the tag from the response url
        response_url = str(response.url)
        tag = re.search(r"explore\/tags\/(.+?)\/", response_url).group(1)
        #gets the total amount of posts to a hashtag
        try:
            post_count = re.search(r"TagPage(?:.+?)media(?:.+?)count\"\: ([0-9]+)", html).group(1)
        except AttributeError:
            try:
                post_count = re.search(r"(?:count\"\: )([0-9]+)(?:\,)(?:.+?)(?:page_info)(?:.+?)(?:end_cursor)", html).group(1)
            except AttributeError:
                post_count = re.search(r"(?:media\"\: \{\"count\"\: )([0-9]+)", html).group(1)

        #TOP POSTS
        #current date time - when top post was posted to see how long it takes
        #return code, date, width, height, comment_count, owner, isvideo, imageid
        top_post_data = extractPostsFromPage(html, top_post=True, response=str(response.url))
        #amount of time it took to get to the top post
        currentTime = time()
        top_post_duration = currentTime - int(top_post_data[1])
        #the tag name, amount of posts, time logged, time_to_top post, all stats of top post
        try:
            cursor.execute('INSERT INTO insta_hashtags (tag, posts, entry_time, time_to_top, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, location, slug) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (tag, int(post_count), int(time()), top_post_duration, top_post_data[0], top_post_data[1], top_post_data[2], top_post_data[3], top_post_data[4], top_post_data[5], top_post_data[6], top_post_data[7], top_post_data[8], top_post_data[9]))
        except Exception as e:
            #print (e)
            pass
        connection.commit()

        url_codes = re.findall(r"\"code\"\: \"(.+?)\"", html)
        for code in url_codes:
            url = "https://www.instagram.com/p/{}/".format(code)
            yield Request(url, callback=self.parseImage)

    def parseImage(self, response):
        #yield Request("https://www.instagram.com/{}/".format(re.search(r"owner\"\: \{(?:.+?)username\"\: \"(.+?)\"", str((response.xpath("//body")).extract())).group(1)), callback=self.parseUser)
        html = str((response.xpath("//body")).extract())

        #all non duplicate usernames from image page aka commenters and the poster
        owner = re.search(r"owner\"\: \{(?:.+?)username\"\: \"(.+?)\"", html).group(1)
        url = "https://www.instagram.com/{}/".format(owner)
        yield Request(url, callback=self.parseUser)


    def parseUser(self, response):
        html = str((response.xpath("//body")).extract())

        #extract things specific to a user
        privacy = str(re.search(r"is\_private\"\: ([a-z]+)", html).group(1))
        username = str(re.search(r"\"username\"\: \"(.+?)\"", html).group(1))
        try:
            post_count = int(re.search(r"\"media\"\: \{\"count\"\: ([0-9]+)", html).group(1))
        except AttributeError:
            post_count = 0
        #private users require a different regex
        if privacy == "true" or post_count == 0:
            code = int(re.search(r"id\"\: \"([0-9]+)", html).group(1))
        else:
            code = int(re.search(r"owner\"(?:.+?)([0-9]+)", html).group(1))
        follower_count = int(re.search(r"followed_by\"\: \{\"count\"\: ([0-9]+)", html).group(1))
        follows_count = int(re.search(r"\"follows\"\: \{\"count\"\: ([0-9]+)", html).group(1)) 
        try:
            verification = str(re.search(r"is_verified\"\: ([a-z]+)", html).group(1))
        except AttributeError:
            verification = "false"
        entry = time()

        valid = True

        if code > 9223372036854775807:
            print((username + " CODE IS BROKEN \n") * 100)
            valid = False
        if post_count > 32767:
            print((username + " POST_COUNT IS BROKEN \n") * 100)
            valid = False
        if follower_count > 2147483647:
            print((username + " FOLLOWER_COUNT IS BROKEN \n") * 100)
            valid = False
        if follows_count > 32767:
            print((username + " FOLLOWS_COUNT IS BROKEN \n") * 100)
            valid = False
        if follows_count > 32767:
            print((username + " FOLLOWS_COUNT IS BROKEN \n") * 100)
            valid = False

        if valid:
            item = InstagramUserItem()
            item["username"] = username 
            item["code"] = code 
            item["post_count"] = post_count 
            item["follower_count"] = follower_count 
            item["follows_count"] = follows_count 
            item["privacy"] = privacy 
            item["verification"] = verification 
            item["entry"] = entry 
            yield item

            extractPostsFromPage(html, response=str(response.url))
'''