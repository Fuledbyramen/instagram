from random import randint
from time import sleep
from subprocess import call

'''
call(["scrapy crawl unlogged_users_conservative_mp -a low='5000000' -a high='5100000'"], shell=True)
sleep(randint(15,45))
call(["scrapy crawl unlogged_users_conservative_mp -a low='5100000' -a high='5200000'"], shell=True)
sleep(randint(15,45))
call(["scrapy crawl unlogged_users_conservative_mp -a low='5200000' -a high='5300000'"], shell=True)
sleep(randint(15,45))
call(["scrapy crawl unlogged_users_conservative_mp -a low='5300000' -a high='5400000'"], shell=True)
sleep(randint(15,45))

'''
print("STARTING")
call(["scrapy crawl unlogged_users_conservative_mp -a low='0' -a high='10'"], shell=True)
