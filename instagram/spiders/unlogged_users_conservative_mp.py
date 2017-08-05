'''
import scrapy
import re
from scrapy import Request, FormRequest
from time import time
import psycopg2


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


def extractPostsFromPage(html, tag="FromUser"):
    global commit_counter, connection

    #all image url codes on the page
    url_codes = re.findall(r"\"code\"\: \"(.+?)\"", html)

    #matches the code to the regex to ensure all regexes are to exact image
    for code in url_codes:
        try:
            caption = re.search(r"{}(?:.+?)caption\"\: \"(.+?)\"\, \"likes".format(code), html).group(1)
        except AttributeError:
            caption = ""
        #try:
        date = int(re.search(r"{}(?:.+?)date\"\: ([0-9]+)".format(code), html).group(1))
        width = int(re.search(r"{}(?:.+?)width\"\: ([0-9]+)".format(code), html).group(1))
        height = int(re.search(r"{}(?:.+?)height\"\: ([0-9]+)".format(code), html).group(1))
        comment_count = int(re.search(r"{}(?:.+?)comments(?:.+?)([0-9]+)".format(code), html).group(1))
        likes = int(re.search(r"{}(?:.+?)\"likes\"\: (?:.+?)count\"\: ([0-9]+)".format(code), html).group(1))
        ownerID = int(re.search(r"{}(?:.+?)owner\"\: (?:.+?)id\"\: \"([0-9]+)".format(code), html).group(1))
        isVideo = re.search(r"{}(?:.+?)likes(?:.+?)is_video\"\: ([a-z]+)".format(code), html).group(1)
        imageID = int(re.search(r"{}(?:.+?)likes(?:.+?)owner(?:.+?)is_video(?:.+?)id\"\: \"([0-9]+)".format(code), html).group(1))
        entry = time()
        #except AttributeError as e:
            #log.write(str(e) + "\n" + code + "\n" + html + "\n")

        cursor.execute('INSERT INTO insta_posts (tag, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
                (tag, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry))

    connection.commit()


class InstagramSpider(scrapy.Spider):
    name = 'mp'
    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = ["https://www.instagram.com"]

    log.write("Starting")

    def parse(self, response):
        start_urls = []
        #5050000 and id < 5150000 To 6m tomorrow.
        #7600000 start
        cursor.execute("SELECT * FROM unlogged_users4 WHERE id > 1760000")
        codes = cursor.fetchall()
        for code in codes:
            start_urls.append("https://www.instagram.com/p/{}/".format(code[1]))
            #cursor.execute("DELETE FROM unlogged_users WHERE id = %s",(code[0],))
        for url in start_urls:
            yield Request(url, callback=self.begin)


    def begin(self, response):
        #take the img url and extract the owner
        html = str((response.xpath("//body")).extract())
        ownerUser = re.search(r"owner(?:.+?)username(?:.+?)([a-z]+)", html).group(1)
        url = "https://www.instagram.com/{}/".format(ownerUser)
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
            print(username + " CODE IS BROKEN \n")
            valid = False
        if post_count > 32767:
            print(username + " POST_COUNT IS BROKEN \n")
            valid = False
        if follower_count > 2147483647:
            print(username + " FOLLOWER_COUNT IS BROKEN \n")
            valid = False
        if follows_count > 32767:
            print(username + " FOLLOWS_COUNT IS BROKEN \n")
            valid = False
        if follows_count > 32767:
            print(username + " FOLLOWS_COUNT IS BROKEN \n")
            valid = False

        if valid:
            cursor.execute('INSERT INTO insta_users (username, code, post_count, follower_count, follows_count, privacy, verification, entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                    (username, code, post_count, follower_count, follows_count, privacy, verification, entry))

            extractPostsFromPage(html)

'''