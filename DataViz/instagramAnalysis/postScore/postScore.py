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


def getHashtags(captions):
	tags = []
	for caption in captions:
		tempTags = re.findall(r"\#(\w+)", caption)
		tags += tempTags
	tags = list(set(tags))
	return tags


def qualityOfHashtag(hashtag, pullData):
	try:
		index = pullData.index(hashtag)
	except ValueError:
		return 0

	if index <= 375:
		return 100
	if index <= 1000:
		return 75
	if index <= 10000:
		return 50
	return 25


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

    return [round(mediaScore, 2), round(shapeScore, 2)]


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


def scoreDates(j):
	user = j["entry_data"]["ProfilePage"][0]["user"]
	followedBy = user["followed_by"]["count"]
	jMedia = user["media"]["nodes"]

	score = 0
	for i in range(len(jMedia)):
		time = jMedia[i]["date"]
		time = datetime.datetime.fromtimestamp(time)
		hour = time.hour
		day = time.weekday()
		score += scoreHour(hour) + scoreDay(day)
	score /= len(jMedia)
	return round(score, 2)

def scoreDay(day):
	#Monday - Thursday
	if day >= 0 and day <= 3:
		return 50
	#If its Friday
	elif day == 4:
		return 25
	#Saturday or Sunday
	else:
		return 0


def scoreHour(hour):
	#Optimal time all in PDT
	if hour >= 9 and hour <= 12:
		return 50
	elif (hour >= 7 and hour < 9) or (hour > 12 and hour <= 14):
		return 37.5
	elif (hour == 23) or (hour >= 0 and hour < 7):
		return 25
	elif (hour > 14 and hour < 18):
		return 12.5
	elif (hour >= 18 and hour <= 22):
		return 0


def getTimeScore(j):
	return scoreDates(j)


def getMediaScore(j):
    #mediaScore ShapeScore
    return getMedia(j)

	
def getQualityScore(captions):
	hashtagData = getHashtags(captions )
	tags = hashtagData

	cursor.execute("SELECT label FROM vocab50k WHERE label != 'UNK' ORDER BY key")
	pull = [i[0] for i in cursor.fetchall()]

	qualityScore = 0
	for tag in tags:
		qualityScore += qualityOfHashtag(tag, pull)
		
	qualityScore /= len(tags)
	return qualityScore


def postScore(j, captions):
	mediaScoreList = getMediaScore(j)

	timeScore = getTimeScore(j)
	mediaScore = mediaScoreList[0]
	qualityScore = getQualityScore(captions)
	shapeScore = mediaScoreList[1]

	#tiem of posting, photo vs video, hashtag quality, square vs landsacpe vs portrait
	vals = [timeScore, mediaScore, qualityScore, shapeScore]

	totalPostScore = sum(vals) / 4

	return [vals, round(totalPostScore, 2)]

