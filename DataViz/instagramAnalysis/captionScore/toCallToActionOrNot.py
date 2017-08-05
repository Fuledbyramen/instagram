import psycopg2
import re


print("Starting")
conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS callsToAction (phrase TEXT, occurence REAL, likesIncrease REAL, commentIncrease REAL, overallEffectiveness REAL)")


'''
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts2 WHERE likes < 1000 LIMIT 10000000")
pull1 = cursor.fetchall()
'''
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts2 WHERE likes < 1000")
pull1 = cursor.fetchall()
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts3 WHERE likes < 1000")
pull2 = cursor.fetchall()
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts4 WHERE likes < 1000")
pull3 = cursor.fetchall()

data = pull1 + pull2 + pull3

data = pull1

def calculatePhraseIncrease(phrase):
	print("Beginning analysis on '" + phrase + "'")
	#sums
	phraseLikes = 0
	phraseComments = 0 
	phraseCount = 0
	nonPhraseLikes = 0
	nonPhraseComments = 0
	nonPhraseCount = 0

	counter = 0
	for d in data:
		if len(re.findall(r"{}".format(phrase), d[0])) > 0:
			if counter < 100:
				counter += 1
				#print(d[0])
			phraseLikes += d[1]
			phraseComments += d[2]
			phraseCount += 1
		else:
			nonPhraseLikes += d[1]
			nonPhraseComments += d[2]
			nonPhraseCount += 1

	#averages 
	phraseLikes /= phraseCount
	phraseComments /= phraseCount
	nonPhraseLikes /= nonPhraseCount
	nonPhraseComments /= nonPhraseCount
	#a decimal percentage of the increase, 120% increase is defined as 1.2
	likesIncrease = phraseLikes / nonPhraseLikes
	commentsIncrease = phraseComments / nonPhraseComments
	occurence = phraseCount / (phraseCount + nonPhraseCount)
	overallEffectiveness = (likesIncrease + commentsIncrease) / 2

	cursor.execute("INSERT INTO callsToAction (phrase, occurence, likesIncrease, commentIncrease, overallEffectiveness) VALUES (%s,%s,%s,%s,%s)",
		(phrase, occurence, likesIncrease, commentsIncrease, overallEffectiveness))
	conn.commit()

	try:
		print("phrases had " + str(phraseLikes) + " likes on average")
		print("phrases had " + str(phraseComments) + " comments on average")
		print("phrases occured " + str(occurence) + " times")

		print("nonPhrases had " + str(nonPhraseLikes) + " likes on average")
		print("nonPhrases had " + str(nonPhraseComments) + " comments on average")
		print("nonPhrases occured " + str(nonPhraseCount / (phraseCount + nonPhraseCount)) + " times")

		print("The phrase increase likes by " + str(likesIncrease * 100) + "%")
		print("The phrase increase comments by " + str(commentsIncrease * 100) + "%")
	except ZeroDivisionError:
		print("Zero Division")


'''
calculatePhraseIncrease(" what do you think")
calculatePhraseIncrease(" does anyone know if")
calculatePhraseIncrease(" comment if")
calculatePhraseIncrease(" let me know if")
calculatePhraseIncrease(" you ")
calculatePhraseIncrease(" tag your ")
calculatePhraseIncrease(" lol ")
calculatePhraseIncrease(" lmao ")
calculatePhraseIncrease(" thoughts?")
calculatePhraseIncrease(" yes or no?")
calculatePhraseIncrease(" what should ")
calculatePhraseIncrease(" rofl ")
calculatePhraseIncrease(" omfg ")
calculatePhraseIncrease(" omg ")
calculatePhraseIncrease(" OMG ")
calculatePhraseIncrease(" think ")
calculatePhraseIncrease(" who ")
calculatePhraseIncrease(" what ")
calculatePhraseIncrease(" when ")
'''
calculatePhraseIncrease("?")
calculatePhraseIncrease(" help")



