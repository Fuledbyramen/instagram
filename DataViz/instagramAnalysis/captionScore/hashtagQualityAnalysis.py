import psycopg2
import re


print("Starting")
conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()
#cursor.execute("CREATE TABLE IF NOT EXISTS callsToAction (phrase TEXT, occurence REAL, likesIncrease REAL, commentIncrease REAL, overallEffectiveness REAL)")

'''
cursor.execute("SELECT label FROM vocab50k WHERE label != 'UNK' ORDER BY key")
hashtagPull = [i[0] for i in cursor.fetchall()]
print(1)
'''
cursor.execute("SELECT label FROM vocab50k WHERE label != 'UNK' AND key <= 375 ORDER BY key")
hashtagPull1 = set([i[0] for i in cursor.fetchall()])

cursor.execute("SELECT label FROM vocab50k WHERE label != 'UNK' AND key > 375 AND key <= 1000 ORDER BY key")
hashtagPull2 = set([i[0] for i in cursor.fetchall()])

cursor.execute("SELECT label FROM vocab50k WHERE label != 'UNK' AND key > 1000 AND key <= 10000 ORDER BY key")
hashtagPull3 = set([i[0] for i in cursor.fetchall()])

cursor.execute("SELECT label FROM vocab50k WHERE label != 'UNK' AND key > 10000 AND key <= 20000 ORDER BY key")
hashtagPull4 = set([i[0] for i in cursor.fetchall()])

cursor.execute("SELECT label FROM vocab50k WHERE label != 'UNK' AND key > 20000 AND key <= 50000 ORDER BY key")
hashtagPull5 = set([i[0] for i in cursor.fetchall()])

cursor.execute("SELECT caption, likes, commentCount FROM insta_posts2 WHERE likes < 1000")
pull1 = cursor.fetchall()
print(2)
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts3 WHERE likes < 1000")
pull2 = cursor.fetchall()
print(3)
cursor.execute("SELECT caption, likes, commentCount FROM insta_posts4 WHERE likes < 1000")
pull3 = cursor.fetchall()
print(4)

data = pull1 + pull2 + pull3
data = set(data)

#Parralel arrays containing [amt,likes,comments]

top375 = [0,0,0]
top1000 = [0,0,0]
top10000 = [0,0,0]
top20000 = [0,0,0]
top50000 = [0,0,0]
others = [0,0,0]

lists = [top375, top1000, top10000, top20000, top50000, others]

count = 0
#24.1s

for post in data:

    count += 1
    if count % 100000 == 0:
        print(str(count) + "/" + str(len(data)))

    caption = post[0]
    likes = post[1]
    comments = post[2]

    hashtags = re.findall(r"(?:\#)(\w+)", caption)

    #For each tag within the induividual post's caption
    for tag in hashtags:
        '''
        try:
            index = hashtagPull.index(tag)

        except ValueError:
            index = 250000
        '''

        #if index <= 375:
        if tag in hashtagPull1:
            #adding the sum of two lists, one to the count and the likes and comments
            lists[0] = [x + y for x, y in zip(lists[0], [1, likes, comments])]
        #elif index <= 1000:
        elif tag in hashtagPull2:
            #adding the sum of two lists, one to the count and the likes and comments
            lists[1] = [x + y for x, y in zip(lists[1], [1, likes, comments])]
        #elif index <= 10000:
        elif tag in hashtagPull3:
            #adding the sum of two lists, one to the count and the likes and comments
            lists[2] = [x + y for x, y in zip(lists[2], [1, likes, comments])]
        elif tag in hashtagPull4:
            #adding the sum of two lists, one to the count and the likes and comments
            lists[3] = [x + y for x, y in zip(lists[3], [1, likes, comments])]
        elif tag in hashtagPull5:
            #adding the sum of two lists, one to the count and the likes and comments
            lists[4] = [x + y for x, y in zip(lists[4], [1, likes, comments])]
        else:
            #adding the sum of two lists, one to the count and the likes and comments
            lists[5] = [x + y for x, y in zip(lists[5], [1, likes, comments])]

length = len(data)

#Do for each list
for l in lists:
    l[1] /= l[0]
    l[2] /= l[0]
    print(l)
'''
#Make them averages
top375[1] /= top375[0]
top375[2] /= top375[0]

top1000[1] /= top1000[0]
top1000[2] /= top1000[0]

top10000[1] /= top10000[0]
top10000[2] /= top10000[0]

others[1] /= others[0]
others[2] /= others[0]

print(top375)
print(top1000)
print(top10000)
print(others)
'''

'''


[113972688, 162, 9.643]
[46712174, 162.9, 9.826]
[136095119, 164.597, 10.322]
[308849400, 141.672, 8.14786271238]


[113972688, 162.0022780194497, 9.643070373140624]
[46712174, 162.90709661682627, 9.826483520120473]
[136095119, 164.59765815701297, 10.322697135082413]
[43264904, 165.64658121048876, 10.632896446505463]
[53963079, 160.0918763549426, 9.86954574997472]
[211621417, 132.07363318052066, 7.2007843563395095]
'''



