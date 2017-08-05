import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2
from cycler import cycler
from scipy.interpolate import spline


conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=68.6.201.177")
cursor = conn.cursor()

limit = 1600000
cursor.execute('SELECT DISTINCT ON (code) follower_count FROM insta_users LIMIT %s;', (limit,))

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


bins = [i for i in range(0, 5000, 100)]
#bins = [i for i in range(5000,50000,1000)]



histo = np.histogram(results, bins)
values = histo[0]
bins = histo[1]
x_axis = range(len(bins)-1)

plt.bar(x_axis, values, align='edge', width=1, color=(0/255.,107/255.,164/255.))

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
#plt.xlim(0, 23)

bin_labels = [str(i) for i in bins[::2]]
x_ticker = range(0, len(bins)-1, 2)

xvalues = bin_labels
plt.ticklabel_format(axis='x',style='sci',scilimits=(1,8))
plt.xticks(x_ticker, xvalues, fontsize=14, color="white", rotation=60)
#plt.hist(results, bins, histtype='step')

plt.xlabel('Hour of day', fontsize=18, color='white')
plt.ylabel('Average likes', fontsize=18, color='white')
plt.title('Average likes per hour across {} posts'.format(limit), fontsize=20, color='white')
plt.savefig('FollowerHistogram.png', edgecolor=(0.15294117647058825, 0.1568627450980392, 0.13333333333333333), facecolor=(0.15294117647058825, 0.1568627450980392, 0.13333333333333333))
plt.show()