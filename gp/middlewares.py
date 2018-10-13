# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
NEED_EXAMINATION = 1
JUST_DOWNLOAD = 0
import time

class FirefoxDownloaderMiddleware(object):

    def log(self, err):
        with open('log.text', 'a+') as f:
            f.write(str(err) + '\n')

    def process_request(self,request, spider):
        '''
        this function gets requests and generate response using the webdriver instantiated in the spider
        Totally two kinds of web pages:
            1.web pages with urls that need to invoke selenium functions to adjust page to generate response with
              needed html
            2.web pages that don't need those process
        '''

        def has_result(): #check if any results shown on webpage
            selector = Selector(text=spider.driver.page_source)
            result = selector.xpath('//div[@data-react-server-root-id="12"]/div')
            return result.xpath('./@class').extract()[0] != 'NoResults'

        def check_page_type(url): # check the wabpage need to be clicked or not
            url_split = url.strip().split('/')
            last_dir = url_split[len(url_split) - 1]
            if last_dir == 'include=sold-3mo':
                return NEED_EXAMINATION
            else:
                return JUST_DOWNLOAD

        def find_download_button_and_download():
            element = WebDriverWait(spider.driver, 3).until(
                EC.presence_of_all_elements_located((By.ID, "download-and-save"))
            )
            spider.driver.find_element_by_id("download-and-save").click()
            print('!----------------File Downloaded----------------')

        def click_table_button():
            element = WebDriverWait(spider.driver, 8).until(
                EC.presence_of_all_elements_located((By.ID, "sidepane-header"))
            )
            spider.driver.find_element_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='Photos'])[1]/following::button[1]").click()

        def get_webpage():
            url = request.url
            spider.driver.get(url)

        print('---------------------FireFox driver begin---------------------')
        try:
            get_webpage()
        finally:#ignore timeout
            try:
                if check_page_type(request.url) == NEED_EXAMINATION:

                    if not has_result() :                              #Example page: https://www.redfin.com/zipcode/78562/filter/include=sold-3mo
                        print('-----------------------No Result On This Page-----------------')
                        return
                    else:
                        try:
                            find_download_button_and_download()
                        except:                                         #no download button found
                            print("SELENIUM Exception：No Download Button Exception And Change to table form")
                            try:
                                click_table_button()
                                WebDriverWait(spider.driver, 10).until( #waiting for loading
                                    EC.presence_of_all_elements_located((By.XPATH, "//a[@class='address']"))
                                )
                            except Exception as err:
                                print(err)
                            finally:
                                return HtmlResponse(url=request.url, body=spider.driver.page_source, request=request,
                                                encoding='utf-8',
                                                status=200)
                else:
                    return HtmlResponse(url=request.url, body=spider.driver.page_source, request=request, encoding='utf-8',
                                    status=200)

            except TimeoutException as err:                             #if selenium timeout
                self.log(err)
                return HtmlResponse(url=request.url, body=spider.driver.page_source, request=request, encoding='utf-8', status=200)

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
