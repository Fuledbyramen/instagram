import requests
import re
import json
import psycopg2
import datetime
import calendar


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


def getTimeScore(account):
	html = getHtml(account)
	accData = getData(html, account)
	return scoreDates(accData[0])

print(getTimeScore("kendall_morris"))