import psycopg2
import re


print("Starting")
conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()
#cursor.execute("CREATE TABLE IF NOT EXISTS callsToAction (phrase TEXT, occurence REAL, likesIncrease REAL, commentIncrease REAL, overallEffectiveness REAL)")


'''
cursor.execute("SELECT width, height, likes, commentCount FROM insta_posts2 WHERE likes < 1000 LIMIT 10000000")
pull1 = cursor.fetchall()
'''
cursor.execute("SELECT width, height, likes, commentCount FROM insta_posts2 WHERE likes < 1000")
pull1 = cursor.fetchall()
cursor.execute("SELECT width, height, likes, commentCount FROM insta_posts3 WHERE likes < 1000")
pull2 = cursor.fetchall()
cursor.execute("SELECT width, height, likes, commentCount FROM insta_posts4 WHERE likes < 1000")
pull3 = cursor.fetchall()

data = pull1 + pull2 + pull3

#data = pull1

#list is likes, comments, count
square = [0,0,0]
#Width greater than height
landscape = [0,0,0]
#Height greater than width
portrait = [0,0,0]
#Total counter 
counter = 0

for d in data:
	counter += 1
	#Square
	if d[0] == d[1]:
		square[0] += d[2]
		square[1] += d[3]
		square[2] += 1
	else:
		if d[0] > d[1]:
			landscape[0] += d[2]
			landscape[1] += d[3]
			landscape[2] += 1
		else:
			portrait[0] += d[2]
			portrait[1] += d[3]
			portrait[2] += 1

#averages 
square[0] /= square[2]
square[1] /= square[2]
landscape[0] /= landscape[2]
landscape[1] /= landscape[2]
portrait[0] /= portrait[2]
portrait[1] /= portrait[2]

#a decimal percentage of the increase, 120% increase is defined as 1.2
print("Squares had " + str(square[0]) + " likes on average")
print("Squares had " + str(square[1]) + " comments on average")
print("Landscapes had " + str(landscape[0]) + " likes on average")
print("Landscapes had " + str(landscape[1]) + " comments on average")
print("Portraits had " + str(portrait[0]) + " likes on average")
print("Portraits had " + str(portrait[1]) + " comments on average")


'''
Starting
Squares had 127.12940617652859 likes on average
Squares had 7.6995172343921885 comments on average
Landscapes had 154.2399950950753 likes on average
Landscapes had 8.502655855830001 comments on average
Portraits had 162.62561958681837 likes on average
Portraits had 10.36759969200359 comments on average
[Finished in 207.0s]
'''