import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2
from cycler import cycler
from scipy.interpolate import spline


print("STARTING")
conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS timeOfPosting (day SMALLINT, hour SMALLINT, likes REAL, comments REAL)")
conn.commit()

cursor.execute('SELECT DISTINCT ON (code) date, likes, comment_count FROM insta_posts WHERE likes < 1000')
pull1 = cursor.fetchall()
cursor.execute('SELECT DISTINCT ON (code) date, likes, commentcount FROM insta_posts2 WHERE likes < 1000')
pull2 = cursor.fetchall()
cursor.execute('SELECT DISTINCT ON (code) date, likes, commentcount FROM insta_posts3 WHERE likes < 1000')
pull3 = cursor.fetchall()
cursor.execute('SELECT DISTINCT ON (code) date, likes, commentcount FROM insta_posts4 WHERE likes < 1000')
pull4 = cursor.fetchall()

results = pull1 + pull2 + pull3 + pull4

#results = pull1
limit = len(results)
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

plt.figure(figsize=(30, 10))  
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



# Make sure your axis ticks are large enough to be easily read.    
# You don't want your viewers squinting to read your plot.    
plt.yticks(fontsize=14)    
plt.xticks(fontsize=14) 

#plt.ylim(0, 90)    
plt.xlim(0, 23)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
week = {u : {k : [[],[]] for k in range(24)} for u in range(7)}

for row in results:
    day = datetime.fromtimestamp(row[0]).weekday()
    hour = datetime.fromtimestamp(row[0]).hour
    week[day][hour][0].append(row[1])
    week[day][hour][1].append(row[2])

average = lambda x: sum(x) / len(x)

hours = []
likes = []
comments = []
counter = 0
for day, hour in week.items():
    for i in range(24):
        hours.append(i)
        likes.append(average(week[day][i][0]))

        print(day, i, average(week[day][i][0]), average(week[day][i][1]))
        cursor.execute('INSERT INTO timeOfPosting (day, hour, likes, comments) VALUES (%s,%s,%s,%s)', (day, i, average(week[day][i][0]), average(week[day][i][1])))

    hours = np.array(hours)
    likes = np.array(likes)
    x_smooth = np.linspace(hours.min(), hours.max(), 200)
    y_smooth = spline(hours, likes, x_smooth)
    plt.plot(x_smooth, y_smooth, color=colors[counter], label=days[counter], lw=2.5)
    hours = []
    likes = []
    counter += 1

conn.commit()

legend = plt.legend(loc='upper left', shadow=True)
plt.xticks(np.arange(0, 24, 1.0))
plt.xlabel('Hour of day', fontsize=14)
plt.ylabel('Average likes', fontsize=14)
plt.title('Average likes per hour across {} posts'.format(limit), fontsize=16)
plt.savefig('cleanDaysAndHours.png', transparent=True)
plt.show()
