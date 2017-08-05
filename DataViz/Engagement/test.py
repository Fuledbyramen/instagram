import psycopg2
import requests
import json
import re


conn = psycopg2.connect("dbname=instagram user=postgres password=e5b2z123 host=localhost")
cursor = conn.cursor()

cursor.execute("ALTER TABLE percentile ADD COLUMN comments int[][]")
conn.commit()
  