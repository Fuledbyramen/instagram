import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2


f = open('secret.txt', 'r')
secret = f.read().split(',')
conn = psycopg2.connect(secret[0])
cursor = conn.cursor()

print("Connected")
cursor.execute("SELECT date, likes, code FROM insta_posts WHERE likes > 100 LIMIT 1000000")
print("Gottem")
results = cursor.fetchall()

average = lambda x: sum(x) / len(x)

likes_by_hour = {k: [] for k in range(24)}

for row in results:
    hour = datetime.fromtimestamp(row[0]).hour
    likes_by_hour[hour].append((row[1], row[0]))

likes_by_minute = {k: [] for k in range(1440)}



for i in likes_by_hour:
	additive = i * 60
	for j in likes_by_hour[i]:
		likes_by_minute[datetime.fromtimestamp(j[0]).minute + additive].append(j[1])

minutes = []
values = []

for i in list(likes_by_minute):
	if likes_by_minute[i] == []:
		del likes_by_minute[i]

for minute, likes in likes_by_minute.items():

	try:
		values.append(average(likes))
		minutes.append(minute)
	except IndexError:
		pass
	except ZeroDivisionError:
		pass


plt.plot(minutes, values)
plt.show()
