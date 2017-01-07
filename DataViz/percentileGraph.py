import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2
from cycler import cycler
from scipy.interpolate import spline
import psycopg2
import re



conn = psycopg2.connect("dbname=instagram user=postgres password=e5b2z123 host=70.181.171.158")
cursor = conn.cursor()

cursor.execute("SELECT percentile, high FROM percentile WHERE percentile < 99")
percentiles = cursor.fetchall()

colors = [(31, 119, 180), (174, 199, 232)]
for i in range(len(colors)):    
    r, g, b = colors[i]    
    colors[i] = (r / 255., g / 255., b / 255.)

plt.figure(figsize=(24, 10))  
ax = plt.subplot(111)    
ax.spines["top"].set_visible(False)    
ax.spines["bottom"].set_visible(False)    
ax.spines["right"].set_visible(False)    
ax.spines["left"].set_visible(False)    
ax.get_xaxis().tick_bottom()    
ax.get_yaxis().tick_left()    
ax.set_axis_bgcolor((0.15294117647058825, 0.1568627450980392, 0.13333333333333333))  

plt.yticks(fontsize=16, color='white')    
plt.xticks(fontsize=16, color='white') 

plt.xlim(0, 100)
plt.ylim(0,85000)

percentile = []
high = []
for i in percentiles:
    percentile.append(i[0])
    high.append(i[1])

print(high)

percentile = np.array(percentile)
high = np.array(high)


x_smooth = np.linspace(percentile.min(), percentile.max(), 200)
y_smooth = spline(percentile, high, x_smooth)
plt.plot(x_smooth, y_smooth, color=colors[0], label="Percentile", lw=3.5, marker='o', mec="white")
plt.plot(87, 4187, lw=3.5, mew=3.5, color='white', marker='o', mec='white',)

legend = plt.legend(loc='upper left', ncol=2, fancybox=True, frameon=False, fontsize=18)
for text in legend.get_texts():
    plt.setp(text, color="white")
legend.get_frame().set_facecolor((0.15294117647058825, 0.1568627450980392, 0.13333333333333333))

ax.annotate('You are in the 87th percentile \nThis means, given 100 random people\nYou have more followers than 87 of them',
    color="white", xy=(87, 4187), xytext=(70, 19000), arrowprops=dict(facecolor='white', shrink=0.05),)

plt.xticks(np.arange(0, 101, 10.0))
plt.xlabel('Percentile', fontsize=18, color='white')
plt.ylabel('Amount of Followers', fontsize=18, color='white')
#plt.plot(percentile, high, color=colors[0], label="Percentile", lw=3.5)
#plt.plot(high, percentile)
#plt.plot(percentile, high)
plt.savefig('percentileTest.png', edgecolor=(0.15294117647058825, 0.1568627450980392, 0.13333333333333333), facecolor=(0.15294117647058825, 0.1568627450980392, 0.13333333333333333))

plt.show()

