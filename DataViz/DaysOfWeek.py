import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2


f = open('secret.txt', 'r')
secret = f.read().split(',')
conn = psycopg2.connect(secret[0])
cursor = conn.cursor()

query = 'SELECT date, likes FROM insta_posts LIMIT 50000000;'
cursor.execute(query)
results = cursor.fetchall()

likes_by_day = {k: [] for k in range(7)}

for row in results:
    day = datetime.fromtimestamp(row[0]).weekday()
    likes_by_day[day].append(row[1])

average = lambda x: sum(x) / len(x)

for day, likes_list in likes_by_day.items(): 
    print('day: {}, average likes: {}'.format(day, average(likes_list))) 

labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
foo_data = []
for x,y in likes_by_day.items():
	foo_data.append((average(y)))

high = max(foo_data)

bar_width = 0.5
xlocations = np.array(range(len(foo_data))) + bar_width
plt.bar(xlocations, foo_data, width=bar_width, color='grey')
plt.yticks(range(0, int(high + high * 0.1), int(high/10)))
plt.xticks(xlocations + bar_width/2, labels)
plt.xlim(0, xlocations[-1] + bar_width * 2)
plt.title("Likes per day")
plt.gca().get_xaxis().tick_bottom()
plt.gca().get_yaxis().tick_left()
plt.gcf().set_size_inches((8,4))
plt.show()

