import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2
from cycler import cycler


f = open('secret.txt', 'r')
secret = f.read().split(',')
conn = psycopg2.connect(secret[0])
cursor = conn.cursor()

cursor.execute('SELECT date, likes FROM insta_posts LIMIT 50000000;')
results = cursor.fetchall()

colors = ['red', 'green', 'blue', 'yellow', 'orange', 'brown', 'purple']
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
week = {u : {k : [] for k in range(24)} for u in range(7)}

for row in results:
    day = datetime.fromtimestamp(row[0]).weekday()
    hour = datetime.fromtimestamp(row[0]).hour
    week[day][hour].append(row[1])

average = lambda x: sum(x) / len(x)

hours = []
values = []
counter = 0
for day, hour in week.items():
	for i in range(24):
		hours.append(i)
		values.append(average(week[day][i]))
	plt.plot(hours, values, colors[counter], label=days[counter])
	hours = []
	values = []
	counter += 1

legend = plt.legend(loc='upper left', shadow=True)

plt.show()
