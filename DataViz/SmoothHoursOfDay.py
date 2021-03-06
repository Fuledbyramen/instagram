import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2
from cycler import cycler


print("starting")
f = open('secret.txt', 'r')
secret = f.read().split(',')
conn = psycopg2.connect(secret[0])
cursor = conn.cursor()

limit = 10000
cursor.execute('SELECT date, likes FROM insta_posts LIMIT %s;', (limit,))

results = cursor.fetchall()
print("Gottem all")
# These are the "Tableau 20" colors as RGB.    
colors = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]    
  
# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.    
for i in range(len(colors)):    
    r, g, b = colors[i]    
    colors[i] = (r / 255., g / 255., b / 255.)

plt.figure(figsize=(13, 10))  
# Remove the plot frame lines. They are unnecessary chartjunk.    
ax = plt.subplot(111)    
ax.spines["top"].set_visible(False)    
ax.spines["bottom"].set_visible(False)    
ax.spines["right"].set_visible(False)    
ax.spines["left"].set_visible(False)    
  
# Ensure that the axis ticks only show up on the bottom and left of the plot.    
# Ticks on the right and top of the plot are generally unnecessary chartjunk.    
ax.get_xaxis().tick_bottom()    
ax.get_yaxis().tick_left()  
ax.set_axis_bgcolor('black')  
    
# Make sure your axis ticks are large enough to be easily read.    
# You don't want your viewers squinting to read your plot.    
plt.yticks(fontsize=14)    
plt.xticks(fontsize=14) 

#plt.ylim(0, 90)    
#plt.xlim(0, 23)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
week = {u : {k : [] for k in range(1440)} for u in range(7)}

for row in results:
    day = datetime.fromtimestamp(row[0]).weekday()
    hour = datetime.fromtimestamp(row[0]).hour
    minute = datetime.fromtimestamp(row[0]).minute
    hour_part = (hour * 60) + minute
    week[day][hour_part].append(row[1])

def average(x):
	try:
		return sum(x) / len(x)
	except ZeroDivisionError:
		return 0

hours = []
values = []
counter = 0
for day, hour in week.items():
	for i in range(1440):
		hours.append(i)
		values.append(average(week[day][i]))
	plt.plot(hours, values, color=colors[counter], label=days[counter], lw=2.5)
	hours = []
	values = []
	counter += 1

legend = plt.legend(loc='upper left', shadow=True)
plt.xticks(np.arange(0, 1440, 200.0))
plt.xlabel('Hour of day', fontsize=14)
plt.ylabel('Average likes', fontsize=14)
plt.title('Average likes per hour across {} posts'.format(limit), fontsize=16)
plt.show()
