import requests
import re
import json
import psycopg2
import datetime
import calendar



conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=70.181.171.158")
cursor = conn.cursor()


def getHtml(username):
    r = requests.get("https://www.instagram.com/{}/".format(username))
    html = r.text
    return html


#return [json, captions]
def getData(html, username):
    try:
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("/", "\/")
        captions = re.findall(r"caption\"\: \"(.+?)\"\, \"\w+\"\: \{", string)
        try:
            bio = re.search(r"\"biography\"\: \"(.+?)\"\, \"\w+\"\: ", string).group(1)
            string = string.replace(bio, "")
        except AttributeError:
            pass
        for caption in captions:
            string = string.replace(caption, 'c')
        j = json.loads(string)

    except Exception as e:
        i = re.search(r"column ([0-9]+)", str(e)).group(1)
        print(str(e) + "\n " + string[int(i)-20 : int(i)+20] +  "\n" )

        getHtml(username)
        string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("/", "\/")
        captions = re.findall(r"caption\"\: \"(.+?)\"\, \"\w+\"\: \{", html)
        for caption in captions:
            string.replace(caption, 'c')

        j = json.loads(string)

    return [j, captions]


def getMedia(j):
    user = j["entry_data"]["ProfilePage"][0]["user"]
    followedBy = user["followed_by"]["count"]
    jMedia = user["media"]["nodes"]

    mediaScore = 0
    shapeScore = 0

    for i in range(len(jMedia)):
        height = jMedia[i]["dimensions"]["height"]
        width = jMedia[i]["dimensions"]["width"]
        mediaScore += scoreMedia(jMedia[i]["is_video"])
        shapeScore += scoreShape(height, width)

    mediaScore /= len(jMedia)
    shapeScore /= len(jMedia)

    return [mediaScore, shapeScore]


def scoreMedia(boolean):
    if boolean:
        return 85
    return 100


def scoreShape(height, width):
    if width == height:
        return 78
    else:
        #landscape
        if width > height:
            return 95
        #portrait
        else:
            return 100


def mediaScore(account):
    html = getHtml(account)
    accData = getData(html, account)
    print(getMedia(accData[0]))


mediaScore("zach.chao")
