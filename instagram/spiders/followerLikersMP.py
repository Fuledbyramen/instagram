import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
import psycopg2
import json
import logging


#if __name__ == "__main__":
f = open('secret.txt', 'r')
secret = f.read().split(',')

connection = psycopg2.connect(secret[0])
cursor = connection.cursor()

#counters to update the pg tables and for output
user_counter, followSuccess, unfollowSuccess, followFail, unfollowFail = 0, 0, 0, 0, 0

def boolean(string):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        print("Error in boolean function. Neither true nor false.")


class InstagramSpider(scrapy.Spider):
    name = 'followerLikerMP'

    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = ['https://www.instagram.com']

    custom_settings = {"LOG_LEVEL" : "WARNING",
        "CONCURRENT_REQUESTS_PER_DOMAIN" : 1,
        "CONCURRENT_REQUESTS" : 1,
        "DOWNLOAD_DELAY" : 25,
        "AUTOTHROTTLE_ENABLED" : False}

    def __init__(self, user, secret, lastIndex, code, size, action, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.user = user
        self.secret = secret
        self.code = code
        self.lastIndex = lastIndex
        self.size = size
        self.action = action


    #First have to visit instagram.com to get the csrf token
    def parse(self, response):
        html = str((response.xpath("//body")).extract())
        csrf = re.search(r"csrftoken\=(.+?)\;", str(response.headers)).group(1)
        logging.debug(csrf)

        yield FormRequest("https://www.instagram.com/accounts/login/ajax/",
            formdata = {
                'username' : self.user,
                'password' : self.secret
                        },
            headers = {
                'csrftoken' : csrf,
                'x-csrftoken' : csrf,
                'referer' : 'https://www.instagram.com/',
                'cookie' : ('csrftoken=' + csrf),
                'origin': 'https://www.instagram.com',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'authority' : 'www.instagram.com',
                'content-type' : 'application/x-www-form-urlencoded',
                'accept-encoding' : 'gzip, deflate, br',
                'accept-language' : 'en-US,en;q=0.8'
            },
            callback=self.loggedIn,
            dont_filter = True)


    #Log in post has been sent
    def loggedIn(self, response):
        global cursor
        html = str((response.xpath("//body")).extract())
        string = re.search(r"\[\'\<body\>\<p\>(.+?)\<\/p\>\<\/body\>\'\]", html).group(1)
        csrf = re.search(r"csrftoken\=(.+?)\;", str(response.headers)).group(1)
        #sessid = re.search(r"sessionid=(.+?)\;", str(response.headers)).group(1)
        j = json.loads(string)
        
        #Test if the user is logged in correctly or not
        if j["user"] == True and j["authenticated"] == True:
            logging.info("Logged in successfully")

            #This will get the JSON of the 7500 (maximum) users that the user follows
            relationUrl = "https://www.instagram.com/graphql/query/?query_id=17874545323001329&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A{}%7D".format(self.code, 7500)
            print(relationUrl)
            yield Request(relationUrl,
                headers = {
                    'Referer': 'https://www.instagram.com/{}/'.format(self.user),
                    'X-CSRFToken' : csrf,
                },
                callback = self.getFollowingList)
        else:
            logging.critical(string)


    def getFollowingList(self, response):
        cursor.execute("SELECT code, username FROM followList1mBig")
        accounts = cursor.fetchall()

        html = str((response.xpath("//body")).extract())
        csrf = re.search(r"csrftoken\=(.+?)\;", str(response.headers)).group(1)

        followingList = [(int(i), j) for i,j in re.findall(r"\"id\"\: \"([0-9]+)\"\, \"username\"\: \"(\w+)", html)]
        print("LENGTH OF FOLLOWING LIST ----- " + str(len(followingList)))

        #This will hold those to be followed if action is follow
        #If the action is unfollow this will hold those to be unfollowed
        actionList = []

        if self.action == "follow":
            for userTuple in accounts:
                if userTuple not in followingList:
                    actionList.append(userTuple)
        #If unfollowing
        else:
            for userTuple in followingList:      
                if userTuple in accounts:
                    actionList.append(userTuple) 

        #Limit it
        actionList = actionList[:int(self.size)]

        logging.critical("LENGTH OF ACTION LIST ------ " + str(len(actionList)))

        
        #likes = [i for i in range(2, len(actionList), 3)][::-1]
        follows = [i for i in range(1, len(actionList) * 3, 3)]
        tags = [i for i in range(3, len(actionList) * 3, 3)]

        count = len(actionList) - 3

        for code, account in actionList[:int(self.size)]:
            url = "https://www.instagram.com/web/friendships/{}/{}/".format(code, self.action)
            logging.debug(url + " ----- " + str(count))
            yield Request(url, 
                headers = {'Referer': 'https://www.instagram.com/{}/'.format(account),
                    'X-CSRFToken' : csrf,
                },
                method = 'POST',
                meta = {'dont_redirect': True},
                dont_filter = True,
                priority = follows[count],
                callback = self.relationship)

            #This block likes photos
            #Hardcoded tag atm
            tag = "like4like"
            #The url for the tag
            tagUrl = "https://www.instagram.com/explore/tags/{}/".format(tag)
            #Visit the tag url to like a photo
            yield Request(tagUrl,
                headers = {
                    'Referer': 'https://www.instagram.com/',
                    'X-CSRFToken' : csrf,
                },
                meta = {'dont_redirect': True,
                        'count' : tags[count] - 1},
                dont_filter = True,
                priority = tags[count],
                callback = self.getTagPage)

            count -= 1


    def relationship(self, response):
        global followSuccess, unfollowSuccess, followFail, unfollowFail
        html = str(response.xpath("//body").extract())
        csrf = re.search(r"csrftoken\=(.+?)\;", str(response.headers)).group(1)
        typeOfRequest = self.action

        if response.status == 400:
            code = re.search(r"web\/friendships\/([0-9]+)", response.url).group(0)
            cursor.execute("DELETE FROM followList1mBig WHERE code = %s", (code,))
            logging.warning("Removed " + str(code) + " from list")

        try:
            string = re.search(r"body\>\<p\>(.+?)\<\/", html).group(1)
            j = json.loads(string)
            #Log
            if typeOfRequest == "follow":
                followSuccess += 1
                logging.warning(self.user + " ---- " + str(followSuccess) + " follows succesfully sent " + str(followFail) + " follows failed")
            elif typeOfRequest == "unfollow":
                unfollowSuccess += 1
                logging.warning(self.user + " ---- " + str(unfollowSuccess) + " unfollows succesfully sent " + str(unfollowFail) + " unfollows failed")

        except:
            string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\U0001f47b", "").replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("/", "\/")
            j = json.loads(string)
            #Log
            logging.warning(j["status"])
            if typeOfRequest == "follow":
                followFail += 1
                logging.warning(self.user + " ---- " + str(followSuccess) + " follows succesfully sent " + str(followFail) + " follows failed")
            elif typeOfRequest == "unfollow":
                unfollowFail += 1
                logging.warning(self.user + " ---- " + str(unfollowSuccess) + " unfollows succesfully sent " + str(unfollowFail) + " unfollows failed")


    def getTagPage(self, response):
        html = str((response.xpath("//body")).extract())
        csrf = re.search(r"csrftoken\=(.+?)\;", str(response.headers)).group(1)
        tag = re.search(r"tags\/(\w+)\/", response.url).group(0)
        print(response.url)
        #Randomly, the 20th photo on the page at the moment
        #Will be a tuple of (photoCode, photoID)
        photoCode =  re.findall(r"\"code\"\: \"(\w+)(?:.+?)id\"\: \"([0-9]+)\"", html)[20]
        photoUrl = "https://www.instagram.com/web/likes/{}/like/".format(photoCode[1])

        yield Request(photoUrl,
            headers = {
                'Referer': 'https://www.instagram.com/p/{}/?tagged={}'.format(photoCode[0], tag),
                'X-CSRFToken' : csrf,
            },
            meta = {'dont_redirect': True},
            priority = response.meta['count'],
            method = 'POST',
            dont_filter = True,
            callback = self.likePhoto)


    def likePhoto(self, response):
        if response.status == 200:
            logging.critical("LIKING PHOTO ---- " + str(response.url))
            logging.info("Liked successfully")
        else:
            logging.warning(str(response.status) + " unsuccesful like at " + str(response.url))



