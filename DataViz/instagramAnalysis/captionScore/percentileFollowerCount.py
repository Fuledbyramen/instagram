import psycopg2
import re
from time import time



conn = psycopg2.connect("dbname=instagram user=postgres password=e5b2z123 host=70.181.171.158")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS percentile (percentile SMALLINT, low INTEGER, high INTEGER)")
conn.commit()

cursor.execute("SELECT DISTINCT ON (code) follower_count FROM insta_users2")
tempCounts = cursor.fetchall()

counts = []
for count in tempCounts:
	counts.append(count[0])
length = len(counts)
print(length)
counts = sorted(counts, key=int)

iterator = length//100
print(iterator)
for i in range(100):
	#print(str(iterator*i) + " " + str(iterator*(i+1)))
	tempList = counts[(iterator*i) : (iterator*(i+1))]
	#cursor.execute("INSERT INTO percentile (percentile, low, high) VALUES (%s,%s,%s)", (i, tempList[0], tempList[len(tempList)-1]))
	print(str(i) + " " + str(tempList[0]) + " " + str(tempList[len(tempList)-1])) 

conn.commit()