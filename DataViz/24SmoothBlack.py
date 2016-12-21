import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2
from cycler import cycler
from scipy.interpolate import spline


print("Starting")
f = open('secret.txt', 'r')
secret = f.read().split(',')
conn = psycopg2.connect(secret[0])
cursor = conn.cursor()

limit = 50000000
#cursor.execute('SELECT date, likes FROM (SELECT DISTINCT ON (code) date, likes, code FROM insta_posts LIMIT %s) AS temp', (limit,))
cursor.execute('SELECT DISTINCT ON (code) date, likes FROM insta_posts LIMIT %s;', (limit,))

results = cursor.fetchall()
print("Gottem Coach")
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

plt.figure(figsize=(24, 10))  
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
ax.set_axis_bgcolor((0.15294117647058825, 0.1568627450980392, 0.13333333333333333))  


# Make sure your axis ticks are large enough to be easily read.    
# You don't want your viewers squinting to read your plot.    
plt.yticks(fontsize=16, color='white')    
plt.xticks(fontsize=16, color='white') 

#plt.ylim(0, 90)    
plt.xlim(0, 23)

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
    for i in range(25):
        if i == 24:
            j = 24
            i = 0
        else:
            j = i
        hours.append(j)
        values.append(average(week[day][i]))
    hours = np.array(hours)
    values = np.array(values)
    x_smooth = np.linspace(hours.min(), hours.max(), 200)
    y_smooth = spline(hours, values, x_smooth)
    plt.plot(x_smooth, y_smooth, color="white", lw=3.5)
    plt.plot(x_smooth, y_smooth, color=colors[counter], label=days[counter], lw=2.5)
    hours = []
    values = []
    counter += 1

legend = plt.legend(loc='upper left', ncol=2, fancybox=True, frameon=False, fontsize=18)
for text in legend.get_texts():
    plt.setp(text, color="white")
legend.get_frame().set_facecolor((0.15294117647058825, 0.1568627450980392, 0.13333333333333333))

plt.xticks(np.arange(0, 25, 2.0))
plt.xlabel('Hour of day', fontsize=18, color='white')
plt.ylabel('Average likes', fontsize=18, color='white')
plt.title('Average likes per hour across {} posts'.format(limit), fontsize=20, color='white')
plt.savefig('24DistinctAllBlackMarker50mWhite3.5.png', edgecolor=(0.15294117647058825, 0.1568627450980392, 0.13333333333333333), facecolor=(0.15294117647058825, 0.1568627450980392, 0.13333333333333333))
plt.show()
