'''

import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
from time import time, sleep
import psycopg2
import json

#if __name__ == "__main__":
f = open('secret.txt', 'r')
secret = f.read().split(',')

log = open('log.txt', 'w')
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


class InstagramSpider(scrapy.Spider):
    name = 'loginSession'

    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = ['https://www.instagram.com']

    custom_settings = {"LOG_LEVEL" : "WARNING",
        "CONCURRENT_REQUESTS_PER_DOMAIN" : 1,
        "CONCURRENT_REQUESTS" : 1,
        "DOWNLOAD_DELAY" : 5,
        "AUTOTHROTTLE_ENABLED" : False}


    def parse(self, response):
        html = str((response.xpath("//body")).extract())
        csrf = re.search(r"csrftoken\=(.+?)\;", str(response.headers)).group(1)
        print(csrf)

        yield Request(url, 
                headers = {'Referer': 'https://www.instagram.com/',
                    'X-CSRFToken' : csrf,
                    },
                
                method = 'POST',
                meta={'dont_redirect': True},
                dont_filter=True,
                callback=self.relationship)




        yield FormRequest("https://www.instagram.com/accounts/login/ajax/",
            formdata = {
                'username' : 'zach.chao',
                'password' : 'e5b2zinsta1'
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


    def loggedIn(self, response):
        global account, cursor
        html = str((response.xpath("//body")).extract())
        string = re.search(r"\[\'\<body\>\<p\>(.+?)\<\/p\>\<\/body\>\'\]", html).group(1)
        csrf = re.search(r"csrftoken\=(.+?)\;", str(response.headers)).group(1)
        #sessid = re.search(r"sessionid=(.+?)\;", str(response.headers)).group(1)
        j = json.loads(string)
        
        if j["user"] == account[0] and j["authenticated"] == True:
            print("Logged in successfully")
            print(response.headers)

            #Was commented out?!?!
            cursor.execute("SELECT code, username FROM testList3 LIMIT 1")
            accounts = cursor.fetchall()
            action = "follow" 

            for i in range(2):
                for code, account in accounts:
                    url = "https://www.instagram.com/web/friendships/{}/{}/".format(code, action)
                    yield Request(url, 
                        headers = {'Referer': 'https://www.instagram.com/{}/'.format(account),
                            'X-CSRFToken' : csrf,
                            },
                        
                        method = 'POST',
                        meta={'dont_redirect': True},
                        dont_filter=True,
                        callback=self.relationship)

                if action == "follow":
                    action = "unfollow"
                else:
                    action = "follow"

        else:
            print(string)


    def relationship(self, response):
        html = str((response.xpath("//body")).extract())
        try:
            string = re.search(r"body\>\<p\>(.+?)\<\/", html).group(1)
            j = json.loads(string)
            #print(j["status"])
        except:
            string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\U0001f47b", "").replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("/", "\/")
            j = json.loads(string)
            #print(j["entry_data"]["ProfilePage"][0]["user"]["followed_by_viewer"])






'''