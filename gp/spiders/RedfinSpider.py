import re
import scrapy
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from gp.settings import FIREFOX_DRIVER_PATH
from gp.items import RedFinItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class RedfinSpider(scrapy.Spider):
    start = True
    name = 'redfin'
    # allowed_domains = ['refin.com','redfin.com/zipcode','redfin.com/sitemap']
    start_urls = ['https://redfin.com/sitemap',]

    def __init__(self):

        options = webdriver.FirefoxOptions()
        ## if want to crawl without browser showing, uncomment the following line of code
        # options.add_argument('--headless')
        profile = webdriver.FirefoxProfile()

        # set proxy(can be ip pool)
        HOST = "200.255.122.170"
        PORT = "8080"
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", HOST)
        profile.set_preference("network.proxy.http_port", int(PORT))
        profile.set_preference("network.proxy.ssl", HOST)
        profile.set_preference("network.proxy.ssl_port", int(PORT))
        profile.set_preference("general.useragent.override", "whater_useragent")
        profile.update_preferences()
        #set download directory and mute the download dialog box of the browser
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir',
                               '/home/zewei/projects/gp/gp/spiders/download')
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
        #instantiate a browser and set timeout
        self.driver = webdriver.Firefox(options=options, executable_path=FIREFOX_DRIVER_PATH, firefox_profile=profile)
        # self.driver.implicitly_wait(10)

    def logerr(self, err):
        '''
        log error
        :param err:
        :return:
        '''
        with open('log.text', 'w') as f:
            f.write(str(err))

    def login(self, url):
        '''
        login the redfin.com automatically(Because redfin.com hides some fields from tourists).
        :param url: the first page url, which visitor can login.
        :return: none
        '''
        print('--------------------login-------------------')
        print("please wait for logging in...")
        try:
            self.driver.get(url)
        finally:
            print("timeout while logging, continue")
        # wait and click sign in button
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[@data-rf-test-name='SignInLink']"))
        )
        log_in_button = self.driver.find_element_by_xpath("//button[@data-rf-test-name='SignInLink']")
        log_in_button.click()

        # wait and click "Countinue with Email" button
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[@data-rf-test-name='submitButton']"))
        )
        self.driver.find_element_by_xpath("//button[@data-rf-test-name='submitButton']").click()
        time.sleep(1)
        self.driver.find_element_by_name("emailInput").clear()
        self.driver.find_element_by_name("emailInput").send_keys("844891180@qq.com")
        self.driver.find_element_by_name("passwordInput").clear()
        self.driver.find_element_by_name("passwordInput").send_keys("Password0!")
        self.driver.find_element_by_name("passwordInput").send_keys(Keys.RETURN)
        time.sleep(2)
        self.start = False
        #speed up during parsing process
        self.driver.set_page_load_timeout(8)

    def start_requests(self):
        '''
        the first url that the crawler start to parse from
        :return: urls to be crawled
        '''
        if self.start:
            self.login(self.start_urls[0])
        yield scrapy.Request(url=self.start_urls[0], callback = self.enter_states)
        # yield scrapy.Request(url="https://www.redfin.com", callback=self.parse)

    def enter_states(self, response):
        '''
        parse page: https://www.redfin.com/sitemap
        Enter each state and generate its url regarding to its all zipcodes
        :return: generate requests with zip urls
        '''
        list = response.xpath("//body/div[1]/div[3]/div[1]/div/div/ul/li")
        for selector in list:
            urlPartial = selector.xpath(".//div/a/@href").extract()[0]
            url = response.urljoin(urlPartial)
            print(url)
            yield scrapy.Request(url=url, callback=self.parse_zip)

    def parse_zip(self, response):
        '''
        parsing page: https://www.redfin.com/sitemap/KY
        yield all requests of zip url
        :param response:
        :return: generate requests with each house's url
        '''
        list = response.xpath('//*[@id="content"]/div[3]/div[1]/div/div[2]/ul/li')
        for selector in list:
            urlPartial = selector.xpath(".//div/a/@href").extract()[0]
            url = response.urljoin(urlPartial)
            url = url + "/filter/include=sold-3mo"
            yield scrapy.Request(url=url, callback=self.parse_estate)

    def parse_estate(self, response):
        '''
        Example page: https://www.redfin.com/zipcode/90007/filter/include=sold-3mo
        :param response:
        :return:
        '''
        for i in self.parse_house_urls(response): #for page 1
            yield i

        # for page2, page3......
        page_info = response.xpath('//div[@data-rf-test-id="react-data-page-number-and-download"]')
        page = page_info.xpath('//span[@class="pageText"]/text()')[0].re('of (.+)')[0]
        page = int(page)
        for i in range(page-1):
            append_url = "/page-"
            append_url += str(i+2)
            url = response.url + append_url
            yield scrapy.Request(url = url, callback=self.parse_house_urls)

    def parse_house_urls(self, response):
        '''
        Example page: https://www.redfin.com/zipcode/19014/filter/include=sold-3mo
        :param response:
        :return:
        '''
        append_urls = response.xpath('.//a[@class="address"]/@href').extract()
        for au in append_urls:
            url = response.urljoin(au)
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        '''
        Extract info as possible
        Example parse page: https://www.redfin.com/PA/Aston/806-Crystle-Rd-19014/home/37962251
        :param response: response from firefox page_sourse with table button clicked
        :return yield one item on the page
        '''
        # list = response.xpath('//div[@data-react-server-root-id="8"]')
        list = response.xpath('//html')
        item = RedFinItem()
        item['daysonmarket'] = '-'
        item['latitude'] = '-'
        item['longitude'] = '-'
        item['url'] = response.url
        try:
            # basic info(very likely to be found)
            item['solddate'] = list.xpath('//div[@class="home-sash"]/div[@class="sash-text"]/text()').re('[0-9].*[0-9]')[0]
        except:
            print('solddate not fount')

        try:
            item['price'] = list.xpath('//div[@data-rf-test-id="abp-price"]/div[@class="statsValue"]')[0].xpath('string(.)')[
                0].extract().strip()
        except:
            print('price not fount')

        try:
            item['baths'] = list.xpath('//div[@data-rf-test-id="abp-baths"]/div[@class="statsValue"]/text()').extract()[0]
        except:
            print('baths not fount')

        try:
            item['beds'] = list.xpath('//div[@data-rf-test-id="abp-beds"]/div[@class="statsValue"]/text()').extract()[0]
        except:
            print('beds not fount')

        try:
            item['yearbuilt'] = list.xpath('//div[@class="more-info"]/div[1]/span[@data-rf-test-id="abp-yearBuilt"]/'
                                           'span[@class="value"]/text()').extract()[0]
        except:
            print('yearbuilt not fount')

        try:
            item['sqft'] = list.xpath('//div[@data-rf-test-id="abp-sqFt"]/span[1]/span[@class="statsValue"]/text()').extract()[0]
        except:
            print('sqft not fount')

        try:
            item['state'] = list.xpath('//span[@class="region"]/text()').extract()[0]
        except:
            print('state not fount')

        try:
            item['city'] = list.xpath('//span[@class="locality"]/text()').extract()[0]
        except:
            print('city not fount')

        try:
            item['address'] = list.xpath('.//span[@class="street-address"]/text()').extract()[0].strip()
        except:
            print('address not fount')

        try:
            item['zipcode'] = list.xpath('//span[@class="postal-code"]/text()').extract()[0]
        except:
            print('zipcode not fount')

        # info likely to be found
        try:
            item['type'] = response.xpath('//div[@class="keyDetailsList"]//*[contains(text(),"Style")]/'
                                          'following-sibling::*/text()').extract()[0]
        except:
            print('type not fount')

        try:
            item['county'] = response.xpath(
                '//div[@class="keyDetailsList"]//*[contains(text(),"County")]/following-sibling::*//text()').extract()[0]
        except:
            print('county not fount')

        # for lotsize(likely not to be found)
        try:
            p = re.compile('(dimension|Size)[^:]*:[^<]*<[^>]*>([^<]+)', re.IGNORECASE)
            item['lotsize'] = response.xpath('//div[contains(text(),"Property / Lot Details")]/following-sibling::*[1]//'
                                             '*[contains(text(), "Lot Information")]/following-sibling::*').re(p)[1]
        except:
            print('lotsize not fount')

        yield item

    def parse(self):
        pass