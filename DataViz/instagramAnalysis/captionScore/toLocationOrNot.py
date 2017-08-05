import psycopg2
import re

conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()
cursor.execute("SELECT location, likes, commentCount FROM insta_posts4")
pull1 = cursor.fetchall()

'''
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts3")
pull2 = cursor.fetchall()
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts4")
pull3 = cursor.fetchall()

data = pull1 + pull2 + pull3
'''
data = pull1

counter = 0
for d in data:
	if d[0] != "None":
		print(d[0])


'''
data = pull1

emoticonLikes = 0
emoticonComments = 0
emoticonCount = 0
nonEmoticonLikes = 0
nonEmoticonComments = 0
nonEmoticonCount = 0

for d in data:
	#If there is an emoticon
	if len(re.findall(r"\\\\u....", d[0])) > 0:
		emoticonLikes += d[1]
		emoticonComments += d[2]
		emoticonCount += 1
	else:
		nonEmoticonLikes += d[1]
		nonEmoticonComments += d[2]
		nonEmoticonCount += 1

print("Emoticons had " + str(emoticonLikes / emoticonCount) + " likes on average")
print("Emoticons had " + str(emoticonComments / emoticonCount) + " comments on average")
print("Emoticons occured " + str(emoticonCount / (emoticonCount + nonEmoticonCount)) + " times")

print("Non emoticons had " + str(nonEmoticonLikes / nonEmoticonCount) + " likes on average")
print("Non emoticons had " + str(nonEmoticonComments / nonEmoticonCount) + " comments on average")
print("Non emoticons occured " + str(nonEmoticonCount / (emoticonCount + nonEmoticonCount)) + " times")

'''

# All
'''
Emoticons had 312.62409638554215 likes on average
Emoticons had 19.55722891566265 comments on average
Emoticons occured 1.532643544024364e-05 times
Non emoticons had 421.61993655977227 likes on average
Non emoticons had 14.147074340832685 likes on average
Non emoticons occured 0.9999846735645598 times
[Finished in 507.5s]
'''