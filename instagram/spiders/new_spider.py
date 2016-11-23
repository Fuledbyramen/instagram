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

        if top_post:
            return code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry
        else:
            cursor.execute('INSERT INTO insta_posts (tag, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
                    (tag, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry))

    connection.commit()


class InstagramSpider(scrapy.Spider):
    name = 'new_spider'
    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = ["https://www.instagram.com"]

    def parse(self, response):
        start_urls = []
        
        cursor.execute("SELECT hashtag FROM partial_hashtags_csv_one LIMIT 3")
        csv = cursor.fetchall()

        hashtags = ""

        for x in csv:
            hashtags += x[0]

        hashtags = list(hashtags)
        hashtags[0] = ""
        hashtags[len(hashtags) - 1] = ""
        hashtags = ("".join(hashtags)).split(",")
        hashtags = list(set(hashtags))

        for tag in hashtags:
            start_urls.append("https://www.instagram.com/explore/tags/{}/".format(tag))

        for url in start_urls:
            yield Request(url, callback=self.parseTag)


    def parseTag(self, response):
        #take hashtag page and parse it
        html = str((response.xpath("//body")).extract())

        response_url = str(response.url)
        tag = re.search(r"explore\/tags\/(.+?)\/", response_url).group(1)

        #gets the total amount of posts to a hashtag
        post_count = re.search(r"\{\"TagPage\"\: \[\{\"tag\"\: \{\"media\"\: \{\"count\"\: ([0-9]+)", html).group(1)
        #TOP POSTS
        #current date time - when top post was posted to see how long it takes
        #return code, date, width, height, comment_count, owner, isvideo, imageid
        top_post_data = extractPostsFromPage(html, top_post=True)
        #amount of time it took to get to the top post
        currentTime = time()
        top_post_duration = currentTime - int(top_post_data[1])
        #the tag name, amount of posts, time logged, time_to_top post, all stats of top post
        try:
            cursor.execute('INSERT INTO insta_hashtags (tag, posts, entry_time, time_to_top, code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (tag, int(post_count), int(time()), top_post_duration, top_post_data[0], top_post_data[1], top_post_data[2], top_post_data[3], top_post_data[4], top_post_data[5], top_post_data[6], top_post_data[7], top_post_data[8], top_post_data[9]))
        except Exception as e:
            print (e.pgerror)
            log.write(e.pgerror)
        connection.commit()

        has_next_page = boolean(str(re.search(r"has_next_page\"\: ([a-z]+)",html).group(1)))
        if has_next_page:
            img_num = 48
            base_url = "https://www.instagram.com/query/"
            beginning_param = "?q=ig_hashtag("
            middle_param = ")%20%7B%20media.after("
            end_param = "%2C%20{})%20%7B%0A%20%20count%2C%0A%20%20nodes%20%7B%0A%20%20%20%20caption%2C%0A%20%20%20%20code%2C%0A%20%20%20%20comments%20%7B%0A%20%20%20%20%20%20count%0A%20%20%20%20%7D%2C%0A%20%20%20%20comments_disabled%2C%0A%20%20%20%20date%2C%0A%20%20%20%20dimensions%20%7B%0A%20%20%20%20%20%20height%2C%0A%20%20%20%20%20%20width%0A%20%20%20%20%7D%2C%0A%20%20%20%20display_src%2C%0A%20%20%20%20id%2C%0A%20%20%20%20is_video%2C%0A%20%20%20%20likes%20%7B%0A%20%20%20%20%20%20count%0A%20%20%20%20%7D%2C%0A%20%20%20%20owner%20%7B%0A%20%20%20%20%20%20id%0A%20%20%20%20%7D%2C%0A%20%20%20%20thumbnail_src%2C%0A%20%20%20%20video_views%0A%20%20%7D%2C%0A%20%20page_info%0A%7D%0A%20%7D&ref=tags%3A%3Ashow".format(img_num)

            end_cursor = re.search(r"\"end\_cursor\"\: \"(.+?)\"", html).group(1)
            data = base_url + beginning_param + tag + middle_param + end_cursor + end_param
            yield Request(data, callback=self.parseHashtag)


    def parseHashtag(self, response):
        #Parses Hashtag Page
        html = str((response.xpath("//body")).extract())
        
        response_url = str(response.url)
        tag = re.search(r"ig\_hashtag\(([a-z]+)", response_url).group(1)
        extractPostsFromPage(html, tag)

        #all image url codes on the page
        url_codes = re.findall(r"\"code\"\: \"(.+?)\"", html)

        #constructs url from url code
        for code in url_codes:
            url = "https://www.instagram.com/p/%s/" % (code)
            yield Request(url, callback=self.parseImage)

    def parseImage(self, response):
        html = str((response.xpath("//body")).extract())

        users_urls = []
        #all non duplicate usernames from image page aka commenters and the poster
        users_in_html = list(set(re.findall(r"\"username\"\: \"(.+?)\"", html)))
        for user in users_in_html:
            users_urls.append("https://www.instagram.com/%s/" % user)
        users_urls = list(set(users_urls))
        for url in users_urls:
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

