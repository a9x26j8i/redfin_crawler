import os
import csv
import scrapy
from selenium import webdriver
from gp.items import RedFinItem


class ClearnerSpider(scrapy.Spider):
    name = 'cleaner'

    def __init__(self):
        self.driver = webdriver.Firefox()

    def start_requests(self):
        url = "file:" + os.getcwd()+ "/finishing.html"
        yield scrapy.Request(url=url, callback=self.process_data)
    def process_data(self, response):
        path = os.getcwd() + '/spiders/download'
        filelist = os.listdir(path)
        item = RedFinItem()
        yield item
        for name in filelist:
            filepath = os.getcwd() + "/spiders/download/" + name
            with open(filepath, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    item = RedFinItem()
                    item['url'] = row[
                        'URL (SEE http://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)']
                    item['solddate'] = row['SOLD DATE']
                    item['daysonmarket'] = row['DAYS ON MARKET']
                    item['price'] = row['PRICE']
                    item['baths'] = row['BATHS']
                    item['beds'] = row['BEDS']
                    item['yearbuilt'] = row['YEAR BUILT']
                    item['sqft'] = row['SQUARE FEET']
                    item['type'] = row['PROPERTY TYPE']
                    item['lotsize'] = row['LOT SIZE']
                    item['state'] = row['STATE']
                    item['city'] = row['CITY']
                    item['address'] = row['ADDRESS']
                    item['latitude'] = row['LATITUDE']
                    item['longitude'] = row['LONGITUDE']
                    item['zipcode'] = row['ZIP']
                    yield item
        print("filelist:")
        print(filelist)
        #remove all temp file in download dir
        for name in filelist:
            filepath = os.getcwd()+"/spiders/download/" + name
            os.remove(filepath)
        print("-------------------FINISH CLEANING------------------------")