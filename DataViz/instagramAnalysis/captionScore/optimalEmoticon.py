import psycopg2
import re

conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts2 WHERE KEY < 10")
data = cursor.fetchall()
print(data)

'''
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

'''
