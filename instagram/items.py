# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

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

class InstagramHashtagItem2(scrapy.Item):
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

#if the photo is taken from a hashtag there is a possibility location, slug and ad will be filled
#if the photo is taken from a user the location slug and is ad will always be null
class InstagramPostItem2(scrapy.Item):
	tag = Field() 
	code = Field() 
	date = Field() 
	width = Field() 
	height = Field() 
	commentCount = Field() 
	caption = Field() 
	likes = Field() 
	ownerID = Field() 
	ownerUser = Field()
	isVideo = Field()
	videoViews = Field()
	imageID = Field() 
	location = Field()
	slug = Field()
	ad = Field()
	entry = Field()
	userTags = Field()

	

class InstagramUserItem(scrapy.Item):
	username = Field()  
	code = Field() 
	post_count = Field() 
	follower_count = Field() 
	follows_count = Field() 
	privacy = Field() 
	verification = Field() 
	entry = Field()

class InstagramUserItem2(scrapy.Item):
	username = Field()  
	code = Field() 
	postCount = Field() 
	followerCount = Field() 
	followsCount = Field() 
	privacy = Field() 
	verification = Field()
	bio = Field() 
	entry = Field()
