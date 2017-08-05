from subprocess import call
from multiprocessing import Pool
#from itertools import starmap
from time import sleep
import sys
import psycopg2

conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()

cursor.execute("SELECT * FROM botUsers")
pull = cursor.fetchall()

accountIter = [i for i in range(len(pull))]

wd = "C:/Users/zachc/Desktop/instagram_bot/instagram/spiders"

#def run(i, user, secret, lastIndex, size, action):
def run(i):
	cursor.execute("SELECT * FROM botUsers WHERE key = %s", (i,))
	account = cursor.fetchall()
	print(account)
	sys.stdout.flush()

	user = account[0][1]
	print(user)
	secret = account[0][2]
	code = account[0][3]
	lastIndex = account[0][4]
	size = account[0][5]
	action = account[0][6]

	print(action)

	while True:
		call(["scrapy", "crawl", "followerLikerMP", "-a", "user={}".format(user), "-a",
			"secret={}".format(secret), "-a", "code={}".format(code), "-a", 
			"lastIndex={}".format(lastIndex), "-a", "size={}".format(size), "-a", 
			"action={}".format(action)], shell=True, cwd=wd)

		if action == "follow":
			cursor.execute("UPDATE botUsers SET action = 'unfollow' WHERE username = %s", (user,))
			action = "unfollow"
		else:
			cursor.execute("UPDATE botUsers SET action = 'follow' WHERE username = %s", (user,))
			action = "follow"

	#scrapy crawl followerLikerMP -a user=user -a secret=secret -a lastIndex=0 -a size=2500 -a action=follow
	
if __name__ == "__main__":
	#starmap(run, accounts)
	p = Pool(len(pull))
	p.map(run, accountIter)


	