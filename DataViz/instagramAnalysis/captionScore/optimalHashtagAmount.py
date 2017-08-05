#Problem - Find out if photos with more hashtags get more likes and comments
#1 - For each percentile
#2 Calculate the average hashtags
#3 For those above that number - 
	# take average percentile of likes and comments
	# those below, the same

import psycopg2
import re

conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS optimalHashtagAmount (hashtagNum INT, amount INT, likes INT, comments INT)")

cursor.execute("SELECT caption, likes, commentCount FROM insta_posts2 WHERE likes < 1000")
pull2 = cursor.fetchall()
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts3 WHERE likes < 1000")
pull3 = cursor.fetchall()
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts4 WHERE likes < 1000")
pull4 = cursor.fetchall()

data =  pull2 + pull3 + pull4

#Each amount of hashtags has a list
#This list is number, amount, likes, comments
tagCountDict = {n : [n,0,0,0] for n in range(100)}

for d in data:
	tagCount = len(re.findall(r"\#\w+", d[0]))
	likes = d[1]
	commentCount = d[2]
	try:
		tagCountDict[tagCount][1] += 1
		tagCountDict[tagCount][2] += likes
		tagCountDict[tagCount][3] += commentCount
	except KeyError:
		print(tagCount)

for i in range(100):
	try:
		tagCountDict[i][2] = tagCountDict[i][2] / tagCountDict[i][1]
		tagCountDict[i][3] = tagCountDict[i][3] / tagCountDict[i][1]
	except ZeroDivisionError:
		pass

print(tagCount)
for i in range(20):
	print(tagCountDict[i])	
	cursor.execute("INSERT INTO optimalHashtagAmount (hashtagNum, amount, likes, comments) VALUES (%s,%s,%s,%s               jjj)",
		(i, tagCountDict[i][0], tagCountDict[i][1], tagCountDict[i][2]))

conn.commit()
'''
Gottem Coach
[359676, 416.53170353317984, 14.252680189948732]
[87662, 582.5627980196665, 16.315256325431772]
[55252, 535.1759755302976, 14.869470788387751]
[53760, 464.1532738095238, 12.69380580357143]
[43883, 355.3703712143655, 10.16211289109678]
[36807, 312.03273833781617, 10.076181161192164]
[30293, 261.0859604529099, 9.350146898623445]
[26001, 278.48471212645666, 9.023152955655553]
[22256, 254.52830697340042, 8.927210639827463]
[19519, 279.493416670936, 9.695988524002255]
[Finished in 409.9s]
'''