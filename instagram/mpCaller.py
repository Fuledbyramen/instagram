from subprocess import call
from multiprocessing import Pool
from time import sleep

wd = "C:/Users/zachc/Desktop/instagram_bot/instagram/spiders"
rnge = 50
spiderCount = 40
start = 153000
startingIndicies = []

for i in range(start, start + (rnge * spiderCount), rnge):
	startingIndicies.append(i)

def run(i):
	sleep(startingIndicies.index(i) * 10)
	call(["scrapy", "crawl", "jsonSpiderMP", "-a", "low={}".format(i), "-a", "high={}".format(i+rnge)], shell=True, cwd=wd)
	#scrapy crawl jsonSpiderMP -a low=13000 -a high=13002
	
if __name__ == "__main__":
	p = Pool(spiderCount)
	p.map(run, startingIndicies)

	

#| TAGS LOGGED 451 | USERS LOGGED 17303 | PHOTOS LOGGED 178803 |
#| TAGS LOGGED 442 | USERS LOGGED 17513 | PHOTOS LOGGED 181752 |
#| TAGS LOGGED 434 | USERS LOGGED 17418 | PHOTOS LOGGED 179834 |
#| TAGS LOGGED 445 | USERS LOGGED 18981 | PHOTOS LOGGED 197573 |
#| TAGS LOGGED 459 | USERS LOGGED 19054 | PHOTOS LOGGED 202800 |

#| TAGS LOGGED 291 | USERS LOGGED 14745 | PHOTOS LOGGED 152141 |