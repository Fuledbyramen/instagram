'''
import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
from time import time
import psycopg2


f = open('secret.txt', 'r')
secret = f.read().split(',')
log = open('invalidHashtags.txt', 'w')

connection = psycopg2.connect(secret[0])
cursor = connection.cursor()

commit_counter = 0

def boolean(string):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        print("Error in boolean function. Neither true nor false.")

def extractPostsFromPage(html, tag="FromUser", top_post = False):
    global commit_counter, connection
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
        date = int(re.search(r"{}(?:.+?)date\"\: ([0-9]+)".format(code), html).group(1))
        width = int(re.search(r"{}(?:.+?)width\"\: ([0-9]+)".format(code), html).group(1))
        height = int(re.search(r"{}(?:.+?)height\"\: ([0-9]+)".format(code), html).group(1))
        comment_count = int(re.search(r"{}(?:.+?)comments(?:.+?)([0-9]+)".format(code), html).group(1))
        caption = re.search(r"{}(?:.+?)caption\"\: \"(.+?)\"\, \"likes".format(code), html).group(1)
        likes = int(re.search(r"{}(?:.+?)likes(?:.+?)([0-9]+)".format(code), html).group(1))
        owner = int(re.search(r"{}(?:.+?)owner(?:.+?)([0-9]+)".format(code), html).group(1))
        isvideo = re.search(r"{}(?:.+?)is_video\"\: ([a-z]+)".format(code), html).group(1)
        imageid = int(re.search(r"{}(?:.+?)is_video(?:.+?)id\"\: \"([0-9]+)".format(code), html).group(1))
        entry = time()
        #check if image is already logged

        if top_post:
            return code, date, width, height, comment_count, caption, likes, owner, isvideo, imageid, entry
        else:
            if not top_post:
                #posts are sorted by tags or user id's
                try:
                    cursor.execute('INSERT INTO insta_posts (tag, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (tag, code, date, width, height, comment_count, caption, likes, owner, isvideo, imageid, entry))
                except Exception as e:
                    print (e.pgerror)
                    log.write(e.pgerror)

class PartialHashtag(scrapy.Spider):
    name = "partial_hashtags"

    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = []

    cursor.execute('SELECT * FROM partial_hashtags_sub_one')
    partials = cursor.fetchall()
    for partial in partials:
        start_urls.append("https://www.instagram.com/explore/tags/{}/".format(partial[0]))
    print(len(start_urls))

    def parse(self, response):
        html = str((response.xpath("//body")).extract())
        img_num = 88
        response_url = str(response.url)
        tag = re.search(r"explore\/tags\/(.+?)\/", response_url).group(1)
        cursor.execute("DELETE FROM partial_hashtags_sub_one WHERE hashtag = %s", (tag[0],))

        has_next_page = boolean(str(re.search(r"has_next_page\"\: ([a-z]+)",html).group(1)))
        if has_next_page:
            end_cursor = re.search(r"\"end\_cursor\"\: \"(.+?)\"", html).group(1)
            url = "https://www.instagram.com/query/?q=ig_hashtag({})%20{{%20media.after({}%2C%20{})%20{{%0A%20%20count%2C%0A%20%20nodes%20{{%0A%20%20%20%20caption%2C%0A%20%20%20%20code%2C%0A%20%20%20%20comments%20{{%0A%20%20%20%20%20%20count%0A%20%20%20%20}}%2C%0A%20%20%20%20date%2C%0A%20%20%20%20dimensions%20{{%0A%20%20%20%20%20%20height%2C%0A%20%20%20%20%20%20width%0A%20%20%20%20}}%2C%0A%20%20%20id%2C%0A%20%20%20%20is_video%2C%0A%20%20%20%20likes%20{{%0A%20%20%20%20%20%20count%0A%20%20%20%20}}%2C%0A%20%20%20%20owner%20{{%0A%20%20%20%20%20%20id%0A%20%20%20%20}}%2C%0A%20%20%20%20video_views%0A%20%20}}%2C%0A%20%20page_info%0A}}%0A%20}}&query_id=&ref=tags%3A%3Ashow".format(tag, end_cursor, img_num)
            yield Request(url, callback=self.parseHashtag)
        else:
            extractPostsFromPage(html, tag)
        

    def parseHashtag(self, response):
        connection.commit()
        #Parses Hashtag Page
        if response.status != 200:
            log.write(response.url)
        html = str((response.xpath("//body")).extract())
        response_url = str(response.url)
        tag = re.search(r"ig\_hashtag\(([a-z]+)", response_url).group(1)
        post_count = re.search(r"media(?:.+?)count\"\: ([0-9]+)", html).group(1)
        top_post_data = extractPostsFromPage(html, top_post=True)
        currentTime = time()
        top_post_duration = currentTime - int(top_post_data[1])
        cursor.execute('INSERT INTO insta_hashtags (tag, posts, entry_time, time_to_top, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (tag, int(post_count), int(time()), top_post_duration, top_post_data[0], top_post_data[1], top_post_data[2], top_post_data[3], top_post_data[4], top_post_data[5], top_post_data[6], top_post_data[7], top_post_data[8], top_post_data[9]))




'''




