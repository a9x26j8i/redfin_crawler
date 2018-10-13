# redfin_crawler
## Introduction
This crawler will scrape all houses sold in past 3 months in the U.S and save them into "gp/gp/houses1.csv" and "gp/gp/houses2.csv" which is really easy to store into either MongoDB or MySQL. Temporary downloaded files can be found in "gp/gp/spiders/download"
It will scrape following fields: 
1. url to the house
2. sold date
3. price
4. baths
5. beds
6. yearbuilt
7. sqft
8. lotsize
9. type
10. daysonmarket
11. state 
12. county
13. city
14. address
15. latitude
16. longitude
17. zipcode
However, the website may miss some of the fields and in this condition the field will leave blank.
##PREREQUISITE
Before running "main.py", please install following packages:
1. scrapy
2. csv
3. selenium
4. re
5. time
and please ensure the computer is installed the newest version of firefox
##CRAWLER STRUCTURE
This crawler is scrapy-selenium combined.RedfinSpider yields requests asychronously and process responses from the downloader middleware, this middleware mainly uses selenium.webdriver to generate response(in this way, we can bypass crawler blocking mechanism of redfin.com and get html as we want) The webdriver is instantiated in the spider and function as a downloader in the form of Firefox browser.

