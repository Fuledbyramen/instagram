import psycopg2
import requests
import re
import json
import math
import random



conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=68.6.201.177")
cursor = conn.cursor()

cursor.execute("SELECT percentile, low, high, likes, comments FROM percentile ORDER BY percentile ASC")
percentilePull = cursor.fetchall()

percentileData = [{
	'num' : field[0],
	'low' : field[1],
	'high' : field[2],
} for field in percentilePull]

context = {
	'percentileData' : percentileData,
}

print(context)