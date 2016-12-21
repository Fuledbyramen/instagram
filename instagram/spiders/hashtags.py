import scrapy
import re
from scrapy import Request, FormRequest
from time import time
import psycopg2
from instagram.items import InstagramHashtagItem, InstagramPostItem, InstagramUserItem


'''
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
        ownerID = int(re.search(r"{}(?:.+?)owner(?:.+?)([0-9]+)".format(code), html).group(1))
        isVideo = re.search(r"{}(?:.+?)is_video\"\: ([a-z]+)".format(code), html).group(1)
        imageID = int(re.search(r"{}(?:.+?)is_video(?:.+?)id\"\: \"([0-9]+)".format(code), html).group(1))
        entry = time()
        #check if image is already logged

        if top_post:
            return code, date, width, height, comment_count, caption, likes, ownerID, isVideo, imageID, entry
        else:
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


class hashtags(scrapy.Spider):
    name = "hashtags"

    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = []

    cursor.execute('SELECT * FROM partial_hashtags_sub_one')
    csvs = cursor.fetchall()
'''

    #for csv in csvs:
        #for i in range(len(csv)-1):
            #start_urls.append("https://www.instagram.com/explore/tags/{}/".format(csv[0]))
'''

    for csv in csvs:
        start_urls.append("https://www.instagram.com/explore/tags/{}/".format(csv[0]))
    def parse(self, response):
        html = str((response.xpath("//body")).extract())
        response_url = str(response.url)
        tag = re.search(r"explore\/tags\/(.+?)\/", response_url).group(1)
        if response.status != 200:
            log.write(tag)
        cursor.execute("DELETE FROM partial_hashtags_sub_one WHERE hashtag = %s", (tag,))

        has_next_page = boolean(str(re.search(r"has_next_page\"\: ([a-z]+)",html).group(1)))
        if has_next_page:
            post_count = re.search(r"media(?:.+?)count\"\: ([0-9]+)", html).group(1)
            top_post_data = extractPostsFromPage(html, top_post=True)
            currentTime = time()
            top_post_duration = currentTime - int(top_post_data[1])

            item = InstagramHashtagItem()
            item["tag"] = tag
            item["posts"] = int(post_count)
            item["entry_time"] = int(time())
            item["time_to_top"] = top_post_duration 
            item["code"] = top_post_data[0]
            item["date"] = top_post_data[1] 
            item["width"] = top_post_data[2] 
            item["height"] = top_post_data[3] 
            item["comment_count"] = top_post_data[4] 
            item["caption"] = top_post_data[5] 
            item["likes"] = top_post_data[6] 
            item["ownerID"] = top_post_data[7] 
            item["isVideo"] = top_post_data[8] 
            item["imageID"] = top_post_data[9]
            return item
        else:
            extractPostsFromPage(html, tag)

'''

