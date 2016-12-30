import psycopg2
f = open('C:\\Users\\zachc\\Desktop\\instagram_bot\\instagram\\spiders\\secret.txt', 'r')
secret = f.read().split(',')
connection = psycopg2.connect(secret[0])
cursor = connection.cursor()
log = open('log.txt', 'w')
cursor.execute("CREATE TABLE IF NOT EXISTS insta_posts(tag TEXT, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0), entry NUMERIC(30,10))")
cursor.execute("CREATE TABLE IF NOT EXISTS insta_users(username TEXT,  code BIGINT, post_count SMALLINT, follower_count INTEGER, follows_count SMALLINT, privacy TEXT, verification TEXT, entry NUMERIC(30,10))")
cursor.execute("CREATE TABLE IF NOT EXISTS insta_hashtags(tag TEXT, posts INTEGER, entry_time NUMERIC(30,10), time_to_top INTEGER, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0))")

cursor.execute("CREATE TABLE IF NOT EXISTS insta_posts2 (key SERIAL PRIMARY KEY, tag TEXT, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, commentCount INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, ownerUser TEXT, isVideo TEXT, videoViews INTEGER, imageID NUMERIC(30,0), entry NUMERIC(30,10), location TEXT, slug TEXT, userTags SMALLINT, ad BOOLEAN)")
cursor.execute("CREATE TABLE IF NOT EXISTS insta_users2 (key SERIAL PRIMARY KEY, username TEXT,  code BIGINT, post_count SMALLINT, follower_count INTEGER, follows_count SMALLINT, privacy BOOLEAN, verification BOOLEAN, entry NUMERIC(30,10), bio TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS insta_hashtags2 (tag TEXT, posts INTEGER, entry_time NUMERIC(30,10), time_to_top INTEGER, code TEXT, date INTEGER, width SMALLINT, height SMALLINT, comment_count INTEGER, caption TEXT, likes INTEGER, ownerID BIGINT, isVideo TEXT, imageID NUMERIC(30,0))")


connection.commit()
cursor.close()
connection.close()