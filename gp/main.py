from scrapy import cmdline
import os

def run():
    os.system("scrapy crawl redfin -o houses1.csv")
    os.system("scrapy crawl cleaner -o houses2.csv")
if __name__ == "__main__":
    run()
