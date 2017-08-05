import psycopg2
import re


print("Starting")
conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()
#cursor.execute("CREATE TABLE IF NOT EXISTS callsToAction (phrase TEXT, occurence REAL, likesIncrease REAL, commentIncrease REAL, overallEffectiveness REAL)")


'''
cursor.execute("SELECT isVideo, likes, commentCount FROM insta_posts2 WHERE likes < 1000 LIMIT 10000000")
pull1 = cursor.fetchall()
'''
cursor.execute("SELECT isVideo, likes, commentCount FROM insta_posts2 WHERE likes < 1000")
pull1 = cursor.fetchall()
cursor.execute("SELECT isVideo, likes, commentCount FROM insta_posts3 WHERE likes < 1000")
pull2 = cursor.fetchall()
cursor.execute("SELECT isVideo, likes, commentCount FROM insta_posts4 WHERE likes < 1000")
pull3 = cursor.fetchall()

data = pull1 + pull2 + pull3


#data = pull1

#sums
phraseLikes = 0
phraseComments = 0 
phraseCount = 0
nonPhraseLikes = 0
nonPhraseComments = 0
nonPhraseCount = 0

counter = 0
for d in data:
	if d[0] == 'true':
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

#cursor.execute("INSERT INTO callsToAction (phrase, occurence, likesIncrease, commentIncrease, overallEffectiveness) VALUES (%s,%s,%s,%s,%s)",
	#(phrase, occurence, likesIncrease, commentsIncrease, overallEffectiveness))
#conn.commit()

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
phrases had 123.28435385815932 likes on average
phrases had 7.925505217337259 comments on average
phrases occured 0.07809956953072446 times
nonPhrases had 141.9991787721333 likes on average
nonPhrases had 8.496729470551399 comments on average
nonPhrases occured 0.9219004304692755 times
The phrase increase likes by 86.82046961411957%
The phrase increase comments by 93.27712792087907%
'''