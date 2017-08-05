import psycopg2

conn = psycopg2.connect("dbname=instagram user=postgres password=e5b2z123 host=70.181.171.158")
cursor = conn.cursor()
cursor.execute("SELECT likes, commentcount FROM insta_posts2 WHERE ownerid IN (SELECT code FROM insta_users2 WHERE follower_count > %s AND follower_count < %s)", (199, 200))
print(len(cursor.fetchall()))