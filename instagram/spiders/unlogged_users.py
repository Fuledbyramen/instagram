import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
from time import time
import psycopg2
from instagram.items import InstagramHashtagItem, InstagramPostItem, InstagramUserItem


f = open('secret.txt', 'r')
log = open('log.txt', 'w')
secret = f.read().split(',')

connection = psycopg2.connect(secret[0])
cursor = connection.cursor()

user_counter = 0

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
        ownerID = int(re.search(r"{}(?:.+?)owner(?:.+?)([0-9]+)".format(code), html).group(1))
        isVideo = re.search(r"{}(?:.+?)is_video\"\: ([a-z]+)".format(code), html).group(1)
        imageID = int(re.search(r"{}(?:.+?)is_video(?:.+?)id\"\: \"([0-9]+)".format(code), html).group(1))
        entry = time()

        item = InstagramPostItem()
        item["tag"] = tag   
        item["code"] = code   
        item["date"] = date   
        item["width"] = width   
        item["height"] = height   
        item["comment_count"] = comment_count   
        item["caption"] = caption   
        item["likes"] = likes   
        item["ownerID"] = ownerID   
        item["isVideo"] = isVideo  
        item["imageID"] = imageID   
        item["entry"] = entry  
        return item
    connection.commit()


class InstagramSpider(scrapy.Spider):
    name = 'unlogged_users'

    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = []

    cursor.execute("SELECT * FROM unlogged_users WHERE id > 6000 and id < 100000")
    codes = cursor.fetchall()
    for code in codes:
        start_urls.append("https://www.instagram.com/p/{}/".format(code[1]))
        #cursor.execute("DELETE FROM unlogged_users WHERE id = %s",(code[0],))

    def parse(self, response):
        global user_counter
        html = str((response.xpath("//body")).extract())
        if user_counter % 5 == 0:
            connection.commit()
        user_counter += 1
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
        verification = str(re.search(r"is_verified\"\: ([a-z]+)", html).group(1))
        #commit to the user database
        entry = time()
        try:
            item = InstagramUserItem()
            item["username"] = username 
            item["code"] = code 
            item["post_count"] = post_count 
            item["follower_count"] = follower_count 
            item["follows_count"] = follows_count 
            item["privacy"] = privacy 
            item["verification"] = verification 
            item["entry"] = entry 
            return item
        except Exception as e:
            print (e.pgerror)
            log.write(e.pgerror)
        #then, if the user has more than 12 posts, aka a next page, load all those posts and log them with one network request
        #as long as they also are not private
        has_next_page = boolean(str(re.search(r"has_next_page\"\: ([a-z]+)",html).group(1)))

        if has_next_page and not boolean(privacy):
            end_cursor = str(re.search(r"end_cursor\"\: \"([0-9]+)", html).group(1))
            #all their posts except the most recent 24, why 24?
            #No clue, instagram just prefers it

            if post_count > 124:
                img_num = str(100)
            elif post_count > 224:
                img_num = str(200)
            else:
                img_num = str(post_count - 24)
            if post_count <= 0:
                post_count = 24

            first = "https://www.instagram.com/query/?q=ig_user("
            second = ")%20{%20media.after("
            third = "%2C%20"
            fourth = ")%20{%0A%20%20count%2C%0A%20%20nodes%20{%0A%20%20%20%20caption%2C%0A%20%20%20%20code%2C%0A%20%20%20%20comments%20{%0A%20%20%20%20%20%20count%0A%20%20%20%20}%2C%0A%20%20%20%20comments_disabled%2C%0A%20%20%20%20date%2C%0A%20%20%20%20dimensions%20{%0A%20%20%20%20%20%20height%2C%0A%20%20%20%20%20%20width%0A%20%20%20%20}%2C%0A%20%20%20%20display_src%2C%0A%20%20%20%20id%2C%0A%20%20%20%20is_video%2C%0A%20%20%20%20likes%20{%0A%20%20%20%20%20%20count%0A%20%20%20%20}%2C%0A%20%20%20%20owner%20{%0A%20%20%20%20%20%20id%0A%20%20%20%20}%2C%0A%20%20%20%20thumbnail_src%2C%0A%20%20%20%20video_views%0A%20%20}%2C%0A%20%20page_info%0A}%0A%20}&ref=users%3A%3Ashow"
            #construct post url from all above
            data = first + str(code) + second + end_cursor + third + img_num + fourth        
            yield Request(data, callback=self.parseExtendedUser)

    def parseExtendedUser(self, response):
        #calls the extraction of posts on the extended page
        #needs to be extra function to get the new request I guess
        html = str(response.xpath("//body").extract())
        extractPostsFromPage(html)














