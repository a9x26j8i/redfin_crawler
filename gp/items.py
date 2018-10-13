# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    gp_icon = scrapy.Field()
    gp_name = scrapy.Field()

class GPReviewItem(scrapy.Item):
    avator_url = scrapy.Field()
    user_name = scrapy.Field()

class TrialItem(scrapy.Item):
    brand = scrapy.Field()


class RedFinItem(scrapy.Item):
    url = scrapy.Field()
    solddate = scrapy.Field()
    price = scrapy.Field()
    baths = scrapy.Field()
    beds = scrapy.Field()
    yearbuilt = scrapy.Field()
    sqft = scrapy.Field()
    lotsize = scrapy.Field()
    type = scrapy.Field()
    daysonmarket = scrapy.Field()

    state = scrapy.Field()
    county = scrapy.Field()
    city = scrapy.Field()
    address = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    zipcode = scrapy.Field()

