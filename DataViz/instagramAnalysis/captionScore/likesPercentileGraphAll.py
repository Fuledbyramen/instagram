
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2
from cycler import cycler
from scipy.interpolate import spline


print("Starting")
conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()

cursor.execute('SELECT likes FROM percentile')

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
ax.set_facecolor((0.15294117647058825, 0.1568627450980392, 0.13333333333333333))


# Make sure your axis ticks are large enough to be easily read.
# You don't want your viewers squinting to read your plot.
plt.yticks(fontsize=16, color='white')
plt.xticks(fontsize=16, color='white')

# plt.ylim(0, 90)
plt.xlim(0, 100)

ordinal = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))

for k in range(0,100,6):
	likes = [i[0] for i in results[k][0]]
	nums = np.array([i for i in range(100)])

	x_smooth = np.linspace(nums.min(), nums.max(), 200)
	y_smooth = spline(nums, likes, x_smooth)

	plt.plot(x_smooth, y_smooth, color=colors[k // 10], label=ordinal(k) + " percentile", lw=3.5)
#plt.plot(x_smooth, y_smooth, color=colors[4], lw=3.5)


legend = plt.legend(loc='upper left', ncol=2, fancybox=True, frameon=False, fontsize=18)
for text in legend.get_texts():
    plt.setp(text, color="white")
legend.get_frame().set_facecolor((0.15294117647058825, 0.1568627450980392, 0.13333333333333333))


plt.xticks(np.arange(0, 100, 5))
plt.xlabel('Hashtag Length in Characters', fontsize=18, color='white')
plt.ylabel('Average likes', fontsize=18, color='white')
plt.title('Optimal Caption Length', fontsize=20, color='white')
plt.savefig('test.png', edgecolor=(0.15294117647058825, 0.1568627450980392, 0.13333333333333333), facecolor=(0.15294117647058825, 0.1568627450980392, 0.13333333333333333))
plt.show()
