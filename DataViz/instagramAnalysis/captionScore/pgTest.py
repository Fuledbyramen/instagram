import psycopg2
import re


conn = psycopg2.connect("dbname=Instagram user=postgres password=Wolve$12Return host=localhost")
cursor = conn.cursor()


cursor.execute("SELECT * FROM percentile WHERE percentile = 99")
res = cursor.fetchone()
print(res)
cursor.execute("INSERT INTO percentile (percentile, low, high, likes, comments) VALUES (%s,%s,%s,%s,%s)",
	(res[0], res[1], 999999999, res[3], res[4]))
conn.commit()
cursor.close()
conn.close()
