# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

#14
class InstagramHashtagItem(scrapy.Item):
	tag = Field() 
	posts = Field() 
	entry_time = Field() 
	time_to_top = Field() 
	code = Field() 
	date = Field() 
	width = Field() 
	height = Field() 
	comment_count = Field() 
	caption = Field() 
	likes = Field() 
	ownerID = Field() 
	isVideo = Field() 
	imageID = Field()

#12
class InstagramPostItem(scrapy.Item):
	tag = Field() 
	code = Field() 
	date = Field() 
	width = Field() 
	height = Field() 
	comment_count = Field() 
	caption = Field() 
	likes = Field() 
	ownerID = Field() 
	isVideo = Field()
	imageID = Field() 
	entry = Field()

#8
class InstagramUserItem(scrapy.Item):
	username = Field()  
	code = Field() 
	post_count = Field() 
	follower_count = Field() 
	follows_count = Field() 
	privacy = Field() 
	verification = Field() 
	entry = Field()


