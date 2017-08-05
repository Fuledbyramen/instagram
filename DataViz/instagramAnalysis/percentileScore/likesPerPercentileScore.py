import psycopg2
import re
import requests
import json


conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()


def getFollowedByLikesComments(username):
    r = requests.get("https://www.instagram.com/{}/".format(username))
    html = r.text
    string = re.search(r"sharedData = (.+?)\;\<\/script\>", html).group(1).replace("\\u2800", "").replace("'", '"').replace("\\\\\"", "'").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\\\\\", "\\\\").replace("\\\\\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("\\\\\\", "\\\\").replace("/", "\/")
    captions = re.findall(r"caption\"\: \"(.+?)\"\, \"\w+\"\: \{", string)
    bio = re.search(r"\"biography\"\: \"(.+?)\"\, \"\w+\"\: ", string).group(1)
    string = string.replace(bio, "")
    for caption in captions:
        string = string.replace(caption, "")

    j = json.loads(string)
    user = j["entry_data"]["ProfilePage"][0]["user"]
    followedBy = user["followed_by"]["count"]
    jMedia = user["media"]["nodes"]
    totalLikes = 0
    totalComments = 0

    for i in range(len(jMedia)):
        totalLikes += jMedia[i]["likes"]["count"]
        totalComments += jMedia[i]["comments"]["count"]
    totalLikes /= len(jMedia)
    totalComments /= len(jMedia)

    return [followedBy, totalLikes, totalComments]


def getIndex(n, ray):
    for i in range(len(ray)):
        if n > ray[i][0] and n < ray[i][1]:
            return i
    return 99


def getPercentiles(account):
    accountData = getFollowedByLikesComments(account)
    cursor.execute("SELECT percentile, likes, comments FROM percentile WHERE low < %s AND high > %s", (accountData[0], accountData[0]))
    pull1 = cursor.fetchall()

    percentile = pull1[0][0]
    likePercentileList = pull1[0][1]
    commentPercentileList = pull1[0][2]

    likePercentile = getIndex(accountData[1], likePercentileList)
    commentPercentile = getIndex(accountData[2], commentPercentileList)

    returnVals = [percentile, likePercentile, commentPercentile]

    return returnVals


def percentileScores(percentiles):
    #Polar scale, 50 giving a score of 100, 100 giving score of 0
    # 75 or 25, score of 50
    percentiles[1] = 100 - (abs(percentiles[1] - 50) * 2)
    percentiles[2] = 100 - (abs(percentiles[2] - 50) * 2)
    overallScore = round((percentiles[0] + percentiles[1] + percentiles[2]) / 3, 2)

    returnVals = percentiles + [overallScore]

    return returnVals

print(percentileScores(getPercentiles("zach.chao")))
