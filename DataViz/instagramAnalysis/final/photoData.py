import requests
import re
import json
import psycopg2
import datetime
import calendar

conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=70.181.171.158")
cursor = conn.cursor()

cursor.execute("SELECT label FROM vocab50k WHERE label != 'UNK' ORDER BY key")
hashtagPull = [i[0] for i in cursor.fetchall()]

def getHtml(username):
    r = requests.get("https://www.instagram.com/{}/".format(username))
    html = r.text
    return html


#return [json, captions]
def getData(html, username):
    validData = False
    while not validData:
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
            validData = True

        except Exception as e:
            i = re.search(r"column ([0-9]+)", str(e)).group(1)
            print(str(e) + "\n " + string[int(i)-20 : int(i)+20] +  "\n" )

            html = getHtml(username)
        return [j, captions]


#Optimal amount of hashtags is 1
def hashtagAmountScoreAndIncrease(captions):
    cursor.execute("SELECT avglikes, avgcomments FROM optimalhashtagunrestricted WHERE hashtagnum <= 11")
    results = cursor.fetchall()
    score = 0
    likesIncrease = 0
    commentsIncrease = 0
    count = len(captions)
    for caption in captions:
        hashtagnum = len(re.findall(r"\#\w+", caption))
        if hashtagnum > 11:
            hashtagnum = 11
        if hashtagnum == 0:
            score += 50
            likesIncrease += (results[1][0] / results[0][0])
            commentsIncrease += (results[1][1] / results[0][1])
        else:
            score += (11 - hashtagnum) * 10
            likesIncrease += (results[1][0] / results[hashtagnum][0])
            commentsIncrease += (results[1][1] / results[hashtagnum][1])
    score /= count
    likesIncrease /= count
    commentsIncrease /= count
    return [round(score, 2), round(likesIncrease, 2), round(commentsIncrease, 2)]


def emoticonScoreAndIncrease(captions):
    score = 0
    likesIncrease = 0
    commentsIncrease = 0
    count = len(captions)
    for caption in captions:
        #If no emoticon is found
        if len(re.findall(r"\\u....", caption)) == 0:
            score += 100
            likesIncrease += 1
            commentsIncrease += 1
        else:
            #Add none to score
            likesIncrease +=  1.31
            commentsIncrease += 1.38
    score /= count
    likesIncrease /= count
    commentsIncrease /= count
    return [round(score, 2), round(likesIncrease, 2), round(commentsIncrease, 2)]


#Calculates the average like and comment increase which can be expected from a single caption
#being made to 940 characters
def evalIndivCLIncrease(caption):
    #Removes emotions and replaces them with one character so they wont be read as seven
    caption = re.sub(r'\\u....', 'e ', caption)
    length = len(caption)

    #Round it to the nearest ten, down
    tempBin = int(len(caption)/10) * 10

    cursor.execute("SELECT likes, comments FROM optimalcaptionlength5k")
    pull = cursor.fetchall()

    #The optimal length is 940 characters
    optimalCaptionLength = pull[94]

    #will be formatted as increase of likes and comments in percentage
    increase = [0,0]

    #Becomes innacurate around 1500, just give same response
    if tempBin >= 150:
        #The likes increase
        increase[0] = optimalCaptionLength[0] / pull[150][0]
        #comment increase
        increase[1] = optimalCaptionLength[1] / pull[150][1]
        return increase
    #Is the optimal range so the increase will be kept the same, 0, none
    elif tempBin > 90 and tempBin < 110:
        return increase
    else:
        #increasse in likes
        increase[0] = optimalCaptionLength[0] / pull[tempBin][0]
        #comments increase
        increase[1] = optimalCaptionLength[1] / pull[tempBin][1]
        return increase


def calculateIncreaseExpected(captions):
    sumOfScores = [0,0]
    for caption in captions:
        results = evalIndivCLIncrease(caption)
        sumOfScores = [round((x + y), 2) for x, y in zip(sumOfScores, results)]
    try:
        sumOfScores = [round((x / len(captions)), 2) for x in sumOfScores]
        return sumOfScores
    except ZeroDivisionError:
        return sumOfScores


def calculateOverallCaptionScore(captions):
    sumOfScores = 0;
    for caption in captions:
        sumOfScores += evaluateLengthScore(caption)
    try:
        return round((sumOfScores/len(captions)), 2)
    except ZeroDivisionError:
        return 0


def captionLengthScoreandIncrease(captions):
    increase = calculateIncreaseExpected(captions)
    return [calculateOverallCaptionScore(captions), increase[0], increase[1]]


#Assigns a score out of 100 to a captions length
def evaluateLengthScore(caption):
    #Removes emotions and replaces them with one character so they wont be read as seven
    caption = re.sub(r'\\u....', 'e ', caption)
    length = len(caption)

    #Explanation in header
    if length == 0:
        length = 0
    elif length < 1100 and length > 900:
        length = 100
    elif length < 1000:
        length = (length / 10) + 10
    elif length >  1000 and length < 2201:
        length = abs(((length - 1100) / 10) - 100)
    #If length is above 2200
    else:
        length = 0
    return length
    

def runWithCaptions(captions):
    captionVals = captionLengthScoreandIncrease(captions)
    emoticonVals = emoticonScoreAndIncrease(captions)
    hashtagVals = hashtagAmountScoreAndIncrease(captions)
    
    vals = [captionVals, emoticonVals, hashtagVals]

    overallScore = sum([i[0] for i in vals]) / 3
    overallLikeIncrease = sum([i[1] for i in vals]) / 3
    overallCommentIncrease = sum([i[2] for i in vals]) / 3

    return vals + [overallScore]


#Percentile Of Followers

def getFollowedByLikesComments(j):
    
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


def getPercentiles(j):
    accountData = getFollowedByLikesComments(j)
    cursor.execute("SELECT percentile, likes, comments, low, high FROM percentile WHERE low < %s AND high > %s", (accountData[0], accountData[0]))
    pull1 = cursor.fetchall()

    percentile = pull1[0][0]
    likePercentileList = pull1[0][1]
    commentPercentileList = pull1[0][2]

    likePercentile = getIndex(accountData[1], likePercentileList)
    commentPercentile = getIndex(accountData[2], commentPercentileList)

    returnVals = [percentile, likePercentile, commentPercentile, [pull1[0][3], pull1[0][4]]]

    return returnVals


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


def getMediaScore(j):
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


def scoreTimeStamp(time):
    time = datetime.datetime.fromtimestamp(time)
    hour = time.hour
    day = time.weekday()
    return (scoreHour(hour) + scoreDay(day))

def getTimeScore(j):
    user = j["entry_data"]["ProfilePage"][0]["user"]
    followedBy = user["followed_by"]["count"]
    jMedia = user["media"]["nodes"]

    score = 0
    for i in range(len(jMedia)):
        time = jMedia[i]["date"]
        score += scoreTimeStamp(time)
    score /= len(jMedia)
    return round(score, 2)

    
def getQualityScore(captions):
    global hashtagPull

    hashtagData = getHashtags(captions)
    tags = hashtagData

    qualityScore = 0
    for tag in tags:
        qualityScore += qualityOfHashtag(tag, hashtagPull)
    
    try:
        qualityScore /= len(tags)
    except ZeroDivisionError:
        return qualityScore
    return qualityScore


def getPostScore(j, captions):
    mediaScoreList = getMediaScore(j)

    timeScore = getTimeScore(j)
    mediaScore = mediaScoreList[0]
    qualityScore = getQualityScore(captions)
    shapeScore = mediaScoreList[1]

    #tiem of posting, photo vs video, hashtag quality, square vs landsacpe vs portrait
    vals = [timeScore, mediaScore, qualityScore, shapeScore]

    totalPostScore = sum(vals) / 4

    return [vals, round(totalPostScore, 2)]


def percentileScores(j):
    percentiles = getPercentiles(j)
    #Polar scale, 50 giving a score of 100, 100 giving score of 0
    # 75 or 25, score of 50
    percentiles[1] = 100 - (abs(percentiles[1] - 50) * 2)
    percentiles[2] = 100 - (abs(percentiles[2] - 50) * 2)
    overallScore = round((percentiles[0] + percentiles[1] + percentiles[2]) / 3, 2)

    returnVals = percentiles + [overallScore]

    return returnVals







def generatePhotoData(j, captions):
    user = j["entry_data"]["ProfilePage"][0]["user"]
    followedBy = user["followed_by"]["count"]
    jMedia = user["media"]["nodes"]

    photoData = []

    for i in range(len(jMedia)):
        photo = jMedia[i]
        timeScore = scoreTimeStamp(photo["date"])
        mediaTypeScore = scoreMedia(photo["is_video"])
        qualityScore = getQualityScore(captions[i])
        shapeScore = scoreShape(photo["dimensions"]["height"], photo["dimensions"]["width"])
        capLengthScore = evaluateLengthScore(captions[i])
        emoticonScore = emoticonScoreAndIncrease(captions[i])[0]
        hashtagAmountScore = hashtagAmountScoreAndIncrease(captions[i])[0]

        returnDict = {
            'url' : photo["thumbnail_src"],
            'codeUrl' : "https://www.instagram.com/p/" + photo["code"],

            'timeScore' : timeScore,
            'mediaTypeScore' : mediaTypeScore,
            'qualityScore' : qualityScore,
            'shapeScore' : shapeScore,
            'capLengthScore' : capLengthScore,
            'emoticonScore' : emoticonScore,
            'hashtagAmountScore' : hashtagAmountScore,

            'cumulScore' : ((timeScore + mediaTypeScore + qualityScore + shapeScore
                + capLengthScore + emoticonScore + hashtagAmountScore) / 7)
        }

        photoData.append(returnDict)

    return photoData




html = getHtml("zach.chao")
accData = getData(html, "zach.chao")

generatePhotoData(accData[0], accData[1])



'''            
'cumulScore' : ,
'''