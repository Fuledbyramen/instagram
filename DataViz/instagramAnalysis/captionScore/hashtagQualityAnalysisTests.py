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
others = [0,0,0]

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
            top375 = [x + y for x, y in zip(top375, [1, likes, comments])]
        #elif index <= 1000:
        elif tag in hashtagPull2:
            #adding the sum of two lists, one to the count and the likes and comments
            top1000 = [x + y for x, y in zip(top1000, [1, likes, comments])]
        #elif index <= 10000:
        elif tag in hashtagPull3:
            #adding the sum of two lists, one to the count and the likes and comments
            top10000 = [x + y for x, y in zip(top10000, [1, likes, comments])]
        else:
            #adding the sum of two lists, one to the count and the likes and comments
            others = [x + y for x, y in zip(others, [1, likes, comments])]

length = len(data)

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
[113972688, 217.730073522763, 12.960227763445483]
[46712174, 89.73597590712201, 5.412834104381088]
[136095119, 264.1573555569046, 16.566556340777588]
[308849400, 515.9737449784492, 29.67474334060066]
[Finished in 1512.6s]


[113972688, 162, 9.643]
[46712174, 162.9, 9.826]
[136095119, 164.597, 10.322]
[308849400, 141.672, 8.14786271238]

'''



