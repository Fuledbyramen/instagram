import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2
from cycler import cycler


conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=68.6.201.177")
cursor = conn.cursor()

#cursor.execute('SELECT DISTINCT ON (tag) tag, posts FROM insta_hashtags ORDER BY tag, posts DESC LIMIT 100')
#cursor.execute('SELECT DISTINCT ON (LOWER(tag)) tag, posts FROM insta_hashtags')
#results1 = cursor.fetchall()
cursor.execute('SELECT DISTINCT ON (LOWER(tag)) tag, posts FROM insta_hashtags2')
results = cursor.fetchall()

print(len(results))
results = sorted(results, key=lambda x: x[1], reverse=True)
taglim = 25
results = results[:taglim]

tags = []
posts = []
for result in results:
	tags.append(result[0].title())
	posts.append(result[1])
posts = list(reversed(posts[:taglim]))
tags = list(reversed(tags[:taglim]))
test = [i for i in range(taglim)]

plt.figure(figsize=(30, 10))  
ax = plt.subplot(111)  
ax.spines["top"].set_visible(False)  
ax.spines["right"].set_visible(False)  
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.tick_params(axis=u'both', which=u'both',length=0)

ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()  

xvalues = [i for i in range(0,1000000001,100000000)]
plt.ticklabel_format(axis='x',style='sci',scilimits=(1,8))
plt.xlim(0,1000000001,100000000)
plt.xticks(xvalues, fontsize=14, color="black")  
plt.yticks(test, tags, fontsize=16, color="black")

ax.get_xaxis().get_major_formatter().set_scientific(False)

plt.xlabel("Amount of posts", fontsize=18, color="black")
plt.ylabel("Hashtag", fontsize=18, color="black")
plt.title("Top 25 Hashtags By Popularity", fontsize=20, color="black")
plt.barh(test, posts, align='center', color=(51/255.,122/255.,183/255.), edgecolor="black", height=1)

plt.savefig('Top25HashtagsByPostWeb.png', transparent=True)
plt.show()