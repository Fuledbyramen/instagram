from subprocess import call
from multiprocessing import Pool
from time import sleep

wd = "C:/Users/zachc/Desktop/instagram/instagram/spiders"
rnge = 25
spiderCount = 30
start = 1000
startingIndicies = []

for i in range(start, start + (rnge * spiderCount), rnge):
	startingIndicies.append(i)

def run(i):
	sleep(startingIndicies.index(i) * 10)
	call(["scrapy", "crawl", "jsonSpiderMP", "-a", "low={}".format(i), "-a", "high={}".format(i+rnge)], shell=True, cwd=wd)
	
if __name__ == "__main__":
	p = Pool(spiderCount)
	p.map(run, startingIndicies)

	