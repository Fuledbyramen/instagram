import psycopg2


def percentiles(counts, centile, kind):
	#splits the likes and comment counts for that percentiles posts into
	#100 lists, high and lows being the percentile ranges
	length = len(counts)
	counts = sorted(counts, key=int)

	iterator = length//100
	outputRay = []
	for i in range(100):
		tempList = counts[(iterator*i) : (iterator*(i+1))]
		outputRay.append([tempList[0], tempList[len(tempList)-1]])
	if kind == "likes":
		cursor.execute("UPDATE percentile SET likes = %s WHERE percentile = %s", (outputRay, centile))
		print(centile)
	else:
		cursor.execute("UPDATE percentile SET comments = %s WHERE percentile = %s", (outputRay, centile))

#Establish Conenction
conn = psycopg2.connect("dbname=instagram user=postgres password=e5b2z123 host=localhost")
cursor = conn.cursor()

#low and high represents range for the percentile
#Ex. those between 545 and 563 followers will be in the 51st percentile
cursor.execute("SELECT low, high FROM percentile")
percentilePull = cursor.fetchall()
#Reversed just to make sure its working 
for i in reversed(range(100)):
	#add comment_count, caption length,  
	#width and height?

	#Takes likes and comment count from posts where the owner is within i percentile
	cursor.execute("SELECT likes, commentcount FROM insta_posts2 WHERE ownerid IN (SELECT code FROM insta_users2 WHERE follower_count > %s AND follower_count < %s)", (percentilePull[i][0], percentilePull[i][1]))
	print("Got it " + str(i))
	tempPull = cursor.fetchall()
	likes = [i[0] for i in tempPull]
	comments = [i[1] for i in tempPull]

	#calls percentile
	percentiles(likes, i, "likes")
	percentiles(comments, i, "comments")

	conn.commit()
