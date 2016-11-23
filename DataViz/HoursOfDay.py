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

likes_by_hour = {k: [] for k in range(24)}

for row in results:
    hour = datetime.fromtimestamp(row[0]).hour
    likes_by_hour[hour].append(row[1])

average = lambda x: sum(x) / len(x)

for hour, likes_list in likes_by_hour.items(): 
    print('hour: {}, average likes: {}'.format(hour, average(likes_list))) 

labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
foo_data = []
for x,y in likes_by_hour.items():
	foo_data.append((average(y)))

hours = []
values = []
for hour, likes in likes_by_hour.items():
	hours.append(hour)
	values.append(average(likes))


plt.plot(hours, values)
plt.show()


