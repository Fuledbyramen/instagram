import psycopg2
import re


print("STARTING")
conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS optimalCaptionLength200bin5kClean (length INT, amount INT, likes INT, comments INT)")
conn.commit()
cursor.execute("SELECT DISTINCT ON (code) caption, likes, commentCount FROM insta_posts2 WHERE likes < 1000")
pull1 = cursor.fetchall()
cursor.execute("SELECT DISTINCT ON (code) caption, likes, commentCount FROM insta_posts3 WHERE likes < 1000")
pull2 = cursor.fetchall()
cursor.execute("SELECT DISTINCT ON (code) caption, likes, commentCount FROM insta_posts4 WHERE likes < 1000")
pull3 = cursor.fetchall()

data = pull1 + pull2 + pull3

#data = pull1

#As before, key is the length
#n is the length again, then goes the amounts, likes, comments
#0 will be 0-9, 10, 10-19 etc
captionLengthDict = {n : [n,0,0,0] for n in range(0,5000,200)}

for d in data:
	caption = d[0]
	caption = re.sub(r'\\u....', 'e ', caption)

	tempBin = int(len(caption)/200) * 200
	try:
		count = captionLengthDict[tempBin][1] + 1
		likes = captionLengthDict[tempBin][2] + d[1]
		comments = captionLengthDict[tempBin][3] + d[2]
		captionLengthDict[tempBin] = [tempBin, count, likes, comments]
	except KeyError:
		pass

for value in captionLengthDict:
	value = captionLengthDict[value]
	try:
		value[2] = value[2]/value[1]
	except ZeroDivisionError:
		pass
	try:
		value[3] = value[3]/value[1]
	except ZeroDivisionError:
		pass

for i in range(0,5000,200):
	values = captionLengthDict[i]
	cursor.execute("INSERT INTO optimalCaptionLength200bin5kClean (length, amount, likes, comments) VALUES (%s,%s,%s,%s)",
		(values[0], values[1], values[2], values[3]))

conn.commit()
cursor.close()
conn.close()