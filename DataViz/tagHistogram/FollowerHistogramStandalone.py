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

plt.figure(figsize=(16, 11))

def graph(sub, bins, low, high, step):
	plt.subplot(sub)

	histo = np.histogram(results, bins)
	values = histo[0]
	bins = histo[1]
	x_axis = range(len(bins)-1)

	plt.bar(x_axis, values, align='edge', edgecolor="black", width=1, color=(0/255.,107/255.,164/255.))
	plt.yticks(fontsize=16, color='white')    
	plt.xticks(fontsize=16, color='white') 

	bin_labels = [str(i) for i in bins[::2]]
	x_ticker = range(0, len(bins)-1, 2)

	xvalues = bin_labels
	plt.ticklabel_format(axis='x',style='sci',scilimits=(1,8))
	plt.xticks(x_ticker, xvalues, fontsize=14, color="white", rotation=60)

	plt.xlabel('Follower Count', fontsize=18, color='white')
	plt.ylabel('Amount of people', fontsize=18, color='white')
	plt.title('Amount in range {} - {} Bin Seperation {}'.format(low, high, step), fontsize=20, color='white')

bins = [i for i in range(0, 5000, 100)]
graph(311, bins, 0, 5000, 100)
bins = [i for i in range(5000, 50000,1000)]
graph(312, bins, 5000, 50000, 1000)
bins = [i for i in range(50000, 1000000, 25000)]
graph(313, bins, 50000, 1000000, 25000)


# Remove the plot frame lines. They are unnecessary chartjunk.    
for sub in [311, 312, 313]:
	ax = plt.subplot(sub)    
	ax.spines["top"].set_visible(False)    
	ax.spines["bottom"].set_visible(False)    
	ax.spines["right"].set_visible(False)    
	ax.spines["left"].set_visible(False)    
	ax.get_xaxis().tick_bottom()    
	ax.get_yaxis().tick_left()    
	ax.set_axis_bgcolor((0.15294117647058825, 0.1568627450980392, 0.13333333333333333))  
   
plt.tight_layout(pad=1)
plt.savefig('FollowerHistogramStandalone.png', edgecolor=(0.15294117647058825, 0.1568627450980392, 0.13333333333333333), facecolor=(0.15294117647058825, 0.1568627450980392, 0.13333333333333333))
plt.show()