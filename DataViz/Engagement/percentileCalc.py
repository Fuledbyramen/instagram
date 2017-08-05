import psycopg2
import requests
import json
import re


def average(x):
    if len(x) != 0:
        return sum(x)/len(x)
    else:
        return 0

def likePercentile(username):
    conn = psycopg2.connect("dbname=instagram user=postgres password=e5b2z123 host=localhost")
    cursor = conn.cursor()

    url = "https://www.instagram.com/{}/".format(username)
    r = requests.get(url)
    html = r.text
    string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("/", "\/")
    captions = re.findall(r"caption\"\: \"(.+?)\", \"", string)
    for caption in captions:
        string = string.replace(caption, "")
    j = json.loads(string)
    user = j["entry_data"]["ProfilePage"][0]["user"]
    media = user['media']['nodes']
    likes = average([m['likes']['count'] for m in media])
    comments = average(list(i for i in (m['comments']['count'] for m in media)))
    followed_by = user["followed_by"]["count"]

    cursor.execute("SELECT likes, comments FROM percentile WHERE low <= %s AND high >= %s", (followed_by, followed_by))
    pull = cursor.fetchone()
    if pull == None:
        cursor.execute("SELECT likes, comments FROM percentile WHERE percentile = 99")
        pull = cursor.fetchone()
    likesRay = pull[0]
    commentsRay = pull[1]

    likesPercentile = 99
    commentsPercentile = 99
    for i in reversed(range(100)):
        if likesRay[i][0] <= likes and likesRay[i][1] >= likes:
            likesPercentile = i
        if commentsRay[i][0] <= comments and commentsRay[i][1] >= comments:
            commentsPercentile = i


    print(likesPercentile)
    print(commentsPercentile)


likePercentile("maddie.chao9")