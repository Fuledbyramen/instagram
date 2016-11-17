import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
from time import time
import psycopg2


f = open('secret.txt', 'r')
log = open('log.txt', 'w')
secret = f.read().split(',')

connection = psycopg2.connect(secret[0])
cursor = connection.cursor()

account = [secret[1], secret[2]]

user_counter = 0

def boolean(string):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        print("Error in boolean function. Neither true nor false.")

def regex_with_default(regex, string, group_number, default_return=0):
    try:
        result = int(re.search(regex, string).group(group_number))
    except ValueError:
        result = re.search(regex, string).group(group_number)
    except AttributeError:
        result = default_return
    return result

def extractPostsFromPage(html, tag="FromUser", top_post = False):
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

    connection.commit()


class InstagramSpider(scrapy.Spider):
    name = 'instagram_spider'

    cursor.execute("CREATE TABLE IF NOT EXISTS insta_posts(tag TEXT, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0), entry NUMERIC(30,10))")
    cursor.execute("CREATE TABLE IF NOT EXISTS insta_users(username TEXT,  code BIGINT, post_count SMALLINT, follower_count INTEGER, follows_count SMALLINT, privacy TEXT, verification TEXT, entry NUMERIC(30,10))")
    cursor.execute("CREATE TABLE IF NOT EXISTS insta_hashtags(tag TEXT, posts INTEGER, entry_time NUMERIC(30,10), time_to_top INTEGER, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0))")

    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = ['https://www.instagram.com']

    def parse(self, response):
        html = str((response.xpath("//body")).extract())
        csrf = re.search(r"csrftoken\=(.+?)\;", str(response.headers)).group(1)
        print(csrf)

        yield FormRequest("https://www.instagram.com/accounts/login/ajax/",
            formdata = {
                'username' : account[0],
                'password' : account[1]
                        },
            headers = {
                'csrftoken' : csrf,
                'x-csrftoken' : csrf,
                'referer' : 'https://www.instagram.com/',
                'cookie' : ('csrftoken=' + csrf),
                'authority' : 'www.instagram.com',
                'content-type' : 'application/x-www-form-urlencoded',
                'accept-encoding' : 'gzip, deflate, br',
                'accept-language' : 'en-US,en;q=0.8'
            },
            callback=self.loggedIn,
            dont_filter = True)

    def loggedIn(self, response):
        body = str((response.xpath("//body")).extract())
        
        if re.search(r"authenticated(?:.+?)(true)(?:.+?){}".format(account[0]), body).group(1) == "true":
            print("Logged in successfully")
            url = "https://www.instagram.com"
            yield Request(url, callback=self.redirect)
        else:
            print("Didn't log in.")

    def redirect(self, response):
        hashtags = ['love', 'instagood', 'me', 'tbt', 'cute', 'follow', 'followme', 
        'photooftheday', 'happy', 'tagforlikes', 'beautiful', 'self', 'girl', 'picoftheday', 
        'like', 'smile', 'friends', 'fun', 'like', 'fashion', 'summer', 'instadaily', 'igers', 
        'instalike', 'food', 'swag', 'amazing', 'tflers', 'follow', 'bestoftheday', 'likeforlike', 
        'style', 'wcw', 'family', 'f', 'nofilter', 'lol', 'life', 'pretty', 'repost', 
        'hair', 'my', 'sun', 'art', 'cool', 'followback', 
        'instafollow', 'instasize', 'bored', 'instacool', 'funny', 'mcm', 'instago', 'instasize', 
        'vscocam', 'girls', 'all', 'party', 'music', 'eyes', 'nature', 'beauty', 'night', 'fitness', 
        'beach', 'look', 'nice', 'sky', 'christmas', 'baby', 'selfie', 'like4like']

        start_hashtag_urls = []

        for hashtag in hashtags:
            start_hashtag_urls.append("https://www.instagram.com/explore/tags/%s/" % (hashtag))
        for url in start_hashtag_urls:
                yield Request(url, callback=self.parseStartHashtag)

    def parseStartHashtag(self, response):
        #Takes a hashtag and extends the amount of photos on the page
        html = str((response.xpath("//body")).extract())
        
        img_num = 48
        base_url = "https://www.instagram.com/query/"
        beginning_param = "?q=ig_hashtag("
        middle_param = ")%20%7B%20media.after("
        end_param = "%2C%20{})%20%7B%0A%20%20count%2C%0A%20%20nodes%20%7B%0A%20%20%20%20caption%2C%0A%20%20%20%20code%2C%0A%20%20%20%20comments%20%7B%0A%20%20%20%20%20%20count%0A%20%20%20%20%7D%2C%0A%20%20%20%20comments_disabled%2C%0A%20%20%20%20date%2C%0A%20%20%20%20dimensions%20%7B%0A%20%20%20%20%20%20height%2C%0A%20%20%20%20%20%20width%0A%20%20%20%20%7D%2C%0A%20%20%20%20display_src%2C%0A%20%20%20%20id%2C%0A%20%20%20%20is_video%2C%0A%20%20%20%20likes%20%7B%0A%20%20%20%20%20%20count%0A%20%20%20%20%7D%2C%0A%20%20%20%20owner%20%7B%0A%20%20%20%20%20%20id%0A%20%20%20%20%7D%2C%0A%20%20%20%20thumbnail_src%2C%0A%20%20%20%20video_views%0A%20%20%7D%2C%0A%20%20page_info%0A%7D%0A%20%7D&ref=tags%3A%3Ashow".format(img_num)

        response_url = str(response.url)
        tag = re.search(r"explore\/tags\/(.+?)\/", response_url).group(1)

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

        #extract all hashtags used in captions on hashtag page
        #hashtags taken here may simply be jokes and have one or two photos in them so will not be parsed like a prolific hashtag
        #They will be added to a hashtag database and when the big hashtags are found, they will be added manually for now
        branchHashtags = re.findall(r"\#([A-Za-z]+)", html)
        #Each will be briefly searched to get stats on it for growth each time they are found
        #generate the urls from the branches
        for branch in branchHashtags:
            url = "https://www.instagram.com/explore/tags/{}/".format(branch)
            yield Request(url, callback=self.parseBranchHashtag)

        #constructs url from url code
        for code in url_codes:
            url = "https://www.instagram.com/p/%s/" % (code)
            yield Request(url, callback=self.parseImage)



    def parseBranchHashtag(self, response):
        body = response.xpath("//body")
        html = str(body.extract())
        #the tag from the response url
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

    def parseImage(self, response):
        body = response.xpath("//body")
        html = str(body.extract())

        users = []
        #all non duplicate usernames from image page aka commenters and the poster
        users_in_html = list(set(re.findall(r"\"username\"\: \"(.+?)\"", html)))
        for user in users_in_html:
            url = "https://www.instagram.com/%s/" % user
            yield Request(url, callback=self.parseUser)


    def parseUser(self, response):
        global user_counter
        html = str(response.xpath("//body").extract())

        #commit every five users
        if user_counter % 5 == 0:
            connection.commit()
        user_counter += 1
        #extract things specific to a user
        privacy = str(re.search(r"is\_private\"\: ([a-z]+)", html).group(1))
        user = str(re.search(r"\"username\"\: \"(.+?)\"", html).group(1))
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
        log.write(str(user) + " " + str(code) + " " + str(post_count) + " " + str(follower_count) + " " + str(follows_count) + " " + str(privacy) + " " + str(verification) + " " + str(entry))
        try:
            cursor.execute('INSERT INTO insta_users (username, code, post_count, follower_count, follows_count, privacy, verification, entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                (user, code, post_count, follower_count, follows_count, privacy, verification, entry))
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
        
        if not boolean(privacy) and follows_count > 50:
            url = "https://www.instagram.com/query/?q=ig_user({})%20{{%0A%20%20follows.first(128)%20{{%0A%20%20%20%20count%2C%0A%20%20%20%20page_info%20{{%0A%20%20%20%20%20%20end_cursor%2C%0A%20%20%20%20%20%20has_next_page%0A%20%20%20%20}}%2C%0A%20%20%20%20nodes%20{{%0A%20%20%20%20%20%20id%2C%0A%20%20%20%20%20%20username%0A%20%20%20%20}}%0A%20%20}}%0A}}%0A&ref=relationships%3A%3Afollow_list".format(code)
            yield Request(url, callback=self.pullPartials)
 
    def pullPartials(self, response):
        html = str(response.xpath("//body").extract())
        follows_users = re.findall(r"username(?:.+?)\"(.+?)\"",html)
        for user in follows_users:
            url = "https://www.instagram.com/{}/".format(user)
            yield Request(url, callback=self.parsePartials)

    def parsePartials(self, response):
        html = str(response.xpath("//body").extract())
        privacy = str(re.search(r"is\_private\"\: ([a-z]+)", html).group(1))
        user = str(re.search(r"\"username\"\: \"(.+?)\"", html).group(1))
        #private users require a different regex
        if privacy == "true":
            code = int(re.search(r"id\"\: \"([0-9]+)", html).group(1))
        else:
            code = int(re.search(r"owner\"(?:.+?)([0-9]+)", html).group(1))
        post_count = int(re.search(r"\"media\"\: \{\"count\"\: ([0-9]+)", html).group(1))
        follower_count = int(re.search(r"followed_by\"\: \{\"count\"\: ([0-9]+)", html).group(1))
        follows_count = int(re.search(r"\"follows\"\: \{\"count\"\: ([0-9]+)", html).group(1)) 
        verification = str(re.search(r"is_verified\"\: ([a-z]+)", html).group(1))
        #commit to the user database
        entry = time()
        try:
            cursor.execute('INSERT INTO insta_users (username, code, post_count, follower_count, follows_count, privacy, verification, entry) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                (user, code, post_count, follower_count, follows_count, privacy, verification, entry))
        except Exception as e:
            print (e.pgerror)
        #then, if the user has more than 12 posts, aka a next page, load all those posts and log them with one network request
        #as long as they also are not private
        has_next_page = boolean(str(re.search(r"has_next_page\"\: ([a-z]+)",html).group(1)))

        if has_next_page and not boolean(privacy):
            end_cursor = str(re.search(r"end_cursor\"\: \"([0-9]+)", html).group(1))
            #all their posts except the most recent 24, why 24?
            #No clue, instagram just prefers it

            if post_count > 124:
                img_num = str(100)
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

