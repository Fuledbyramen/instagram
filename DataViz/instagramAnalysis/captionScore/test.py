import requests
import re
import json
import psycopg2
import datetime
import calendar


conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=68.6.201.177")
cursor = conn.cursor()

cursor.execute('SELECT * FROM optimalHashtagUnrestricted WHERE hashtagnum < 12')    
data = cursor.fetchall()


total = 0
for i in data:
    total += i[1]


total = sum([i[1] for i in data])

print(total)

