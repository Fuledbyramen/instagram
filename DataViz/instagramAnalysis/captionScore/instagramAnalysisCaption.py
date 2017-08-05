import requests
import psycopg2
import re


conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()

'''
Assign a score for someone's last twelve captions
Will be based on four things for now
1 - Length
2 - Emoticons or not
3 - Hashtag amount
4 - Calls to action (Not yet implementable)

1 - Optimal caption length is 940 but this is unrealistic
	need to simply stress longer captions are better
	Captions of 0 and 1800 will be given a score of 0/100
	100/100 : 900 - 1100
	90/100  : 800-900 & 1100-1200
	80/100  : 700
	70/100  : 600
	
	as seen in evaluateLength()

2 - Emoticons or not
	If emoticon, score of 0
	If not, score of 100

3 - Hashtag Amount
	Optimal amount is 1
	0-11 is graded
	Above 11 is given an auto 0
	Grade will be 50 for 0 hashtags
	beyond 1, decreasing by 10

'''


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


def getAccountCaptions(username):
	r = requests.get("https://www.instagram.com/{}/".format(username))
	#captions = re.findall(r"caption\"\: \"(.+?)\"\, \{\"|caption\"\: \"(.+?)\"\, \"\w+\"\: \{", r.text)
	captions = re.findall(r"caption\"\: \"(.+?)\"\, \"\w+\"\: \{", r.text)
	return captions


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
	except ZeroDevisionError:
		return sumOfScores


def calculateOverallCaptionScore(captions):
	sumOfScores = 0;
	for caption in captions:
		sumOfScores += evaluateLengthScore(caption)
	try:
		return round((sumOfScores/len(captions)), 2)
	except ZeroDevisionError:
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

def run(username):
	captions = getAccountCaptions(username)
	captionVals = captionLengthScoreandIncrease(captions)
	emoticonVals = emoticonScoreAndIncrease(captions)
	hashtagVals = hashtagAmountScoreAndIncrease(captions)
	
	vals = [captionVals, emoticonVals, hashtagVals]

	overallScore = sum([i[0] for i in vals]) / 3
	overallLikeIncrease = sum([i[1] for i in vals]) / 3
	overallCommentIncrease = sum([i[2] for i in vals]) / 3

	print(vals)

	print(overallScore)
	print(overallLikeIncrease)
	print(overallCommentIncrease)

	return [vals, overallScore]

def runWithCaptions(captions):
	captionVals = captionLengthScoreandIncrease(captions)
	emoticonVals = emoticonScoreAndIncrease(captions)
	hashtagVals = hashtagAmountScoreAndIncrease(captions)
	
	vals = [captionVals, emoticonVals, hashtagVals]

	overallScore = round((sum([i[0] for i in vals]) / 3), 2)
	overallLikeIncrease = sum([i[1] for i in vals]) / 3
	overallCommentIncrease = sum([i[2] for i in vals]) / 3

	print([vals, overallScore])
	return vals + [overallScore]

captionScoreData = runWithCaptions(getAccountCaptions("kelseacritin"))
print(captionScoreData[0][1])