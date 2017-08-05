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
	

def qualityScore(account):
	html = getHtml(account)
	accData = getData(html, account)
	hashtagData = getHashtags(accData[1])
	tags = hashtagData

	cursor.execute("SELECT label FROM vocab50k WHERE label != 'UNK' ORDER BY key")
	pull = [i[0] for i in cursor.fetchall()]

	qualityScore = 0
	for tag in tags:
		qualityScore += qualityOfHashtag(tag, pull)
		
	qualityScore /= len(tags)
	return qualityScore


print(qualityScore("kendall_morris"))