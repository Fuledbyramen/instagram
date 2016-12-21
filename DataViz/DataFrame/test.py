from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from time import time

start = time()

conn = psycopg2.connect("dbname=instagram user=postgres password=e5b2z123 host=70.181.171.158")
cursor = conn.cursor()

cursor.execute('SELECT * FROM insta_users LIMIT 1000000;')
mid = time()
print(time() - start)

engine = create_engine('postgresql://postgres:e5b2z123@70.181.171.158:5432/instagram')
#pd.df.to_sql("test", engine)
df = pd.read_sql_query('SELECT * FROM "insta_users" LIMIT 1000000', con=engine)

print(time() - mid)