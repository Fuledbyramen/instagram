import psycopg2
import re


conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()
#cursor.execute("CREATE TABLE IF NOT EXISTS optimalCaptionLength100bin5k (length INT, amount INT, likes INT, comments INT)")
#conn.commit()
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts2 LIMIT 1000000")
pull1 = cursor.fetchall()
#cursor.execute("SELECT caption, likes, commentCount FROM insta_posts3")
#pull2 = cursor.fetchall()
#cursor.execute("SELECT caption, likes, commentCount FROM insta_posts4")
#pull3 = cursor.fetchall()

#data = pull1 + pull2 + pull3
data = pull1

#As before, key is the percentage
#n is the percentage again, then goes the amounts, likes, comments
#0 will be 0-4, 5, 5-9 etc
captionPercentageDict = {n : [n,0,0,0] for n in range(0,105,5)}

for d in data:
	caption = d[0]
	#Removed of all tags and hashtags
	captionCleaned = re.sub(r'  ', '', re.sub(r'\@\w+|\#\w+', '', caption))
	try:
		tempBin = int((len(captionCleaned)/len(caption))/.05) * 5

		count = captionPercentageDict[tempBin][1] + 1
		likes = captionPercentageDict[tempBin][2] + d[1]
		comments = captionPercentageDict[tempBin][3] + d[2]
		captionPercentageDict[tempBin] = [tempBin, count, likes, comments]
	except ZeroDivisionError:
		pass


for value in captionPercentageDict:
	value = captionPercentageDict[value]
	try:
		value[2] = value[2]/value[1]
	except ZeroDivisionError:
		pass
	try:
		value[3] = value[3]/value[1]
	except ZeroDivisionError:
		pass


for i in range(0,105,5):
	print(captionPercentageDict[i])
