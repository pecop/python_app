import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from collections import defaultdict
from logging import getLogger,  FileHandler, StreamHandler, Formatter, DEBUG
import threading
from concurrent import futures
from scraping import parse_html, scroll_bottom
from selenium.webdriver.common.keys import Keys


logger = getLogger(__name__)
fomatterSetting = Formatter('[%(asctime)s] %(name)s %(threadName)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
# handler = FileHandler('logger.log')
handler = StreamHandler()
# handler = NullHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
handler.setFormatter(fomatterSetting)
logger.addHandler(handler)
logger.propagate = False

# class Category():

#     def __init__(self, url):
#         self.url = url
#         self.soup = parse_html(url)
#         self.categories = []

#     def search_category(self):

#         categoryNodes = self.soup.select('div[class="item util-clearfix"]>h3>a')

#         for node in categoryNodes:
#             element = {
#                 'name': node.text,
#                 'url': 'https:' + node.get('href')
#             }
#             self.categories.append(element)

#     def search_sub_category(self):

#         subCategoryNodes = self.soup.select('ul[class="sub-item-cont util-clearfix"]')

#         for index, ulNode in enumerate(subCategoryNodes):
#             liNodes = ulNode.select('li>a')
#             elements = []
#             for node in liNodes:
#                 element = {
#                     'name': node.text,
#                     'url': 'https:' + node.get('href')
#                 }
#                 elements.append(element)
#             self.categories[index]['sub'] = elements

#     def search_all(self):

#         self.search_category()
#         self.search_sub_category()


# class Search():

#     def __init__(self, condition):
#         self.condition = condition
#         self.keyword = condition['keyword']
#         self.url = condition['url']
#         self.starNumber = condition['starNumber']
#         self.salesNumber = condition['salesNumber']
#         self.stockNumber = condition['stockNumber']
#         self.priceLower = condition['priceLower']
#         self.priceUpper = condition['priceUpper']
#         self.fetchNumber = condition['fetchNumber']
#         self.itemUrls = []

#     def set_price(self, driver):

#         driver.get(self.url)
#         driver.find_element_by_css_selector('#search-key').send_keys(self.keyword)
#         driver.find_element_by_css_selector('input.search-button').click()

#         time.sleep(5)

#         inputs = driver.find_elements_by_css_selector('span.price-input input')
#         inputs[0].send_keys(500)
#         inputs[1].send_keys(1000)
#         driver.find_element_by_css_selector('a.ui-button.narrow-go').click()

#         time.sleep(5)

#         for i in range(10):
#             try:
#                 driver.find_element_by_css_selector('#switcher-info').click()
#                 driver.find_elements_by_css_selector('span.select-item')[1].click()
#                 break
#             except Exception as err:
#                 time.sleep(1)

#         driver.find_element_by_css_selector('a[data-currency="JPY"]').click()
#         driver.find_element_by_css_selector('button[class="ui-button ui-button-primary go-contiune-btn"]').click()

#         time.sleep(5)

#     def get_item_url(self, driver, scrollStep=20):

#         scroll_bottom(driver, scrollStep)
#         items = driver.find_elements_by_css_selector('a.item-title')
#         logger.debug('アイテム数：' + str(len(items)))

#         for item in items:
#             self.itemUrls.append(item.get_attribute('href'))

class Search():

    def __init__(self, url, keyword):
        self.url = url
        self.keyword = keyword
        self.categories = []
        self.sub_categories = []
        self.itemUrls = []

    def set_keyword(self, driver):

        driver.get(self.url)
        driver.find_element_by_css_selector('#search-key').send_keys(self.keyword)
        driver.find_element_by_css_selector('input.search-button').click()
        time.sleep(3)
    
    def set_currency(self, driver):

        for i in range(10):
            try:
                driver.find_element_by_css_selector('#switcher-info').click()
                driver.find_elements_by_css_selector('span.select-item')[1].click()
                break
            except Exception as err:
                time.sleep(1)

        driver.find_element_by_css_selector('a[data-currency="JPY"]').click()
        driver.find_element_by_css_selector('button[class="ui-button ui-button-primary go-contiune-btn"]').click()

        time.sleep(5)     

    def set_price_range(self, driver, price_range):

        priceLower = price_range['priceLower']
        priceUpper = price_range['priceUpper']
        if not(priceLower) or priceLower == '0':
            priceLower = '1'

        lowerInput, upperInput = driver.find_elements_by_css_selector('span.price-input input')

        lowerInput.send_keys(Keys.CONTROL + 'a')
        lowerInput.send_keys(Keys.DELETE)
        lowerInput.send_keys(priceLower)
        upperInput.send_keys(Keys.CONTROL + 'a')
        upperInput.send_keys(Keys.DELETE)
        upperInput.send_keys(priceUpper)
        
        driver.find_element_by_css_selector('a.ui-button.narrow-go').click()

        time.sleep(5)

    def get_category(self, driver):

        try:
            driver.find_element_by_css_selector('div.show-more').click()
        except Exception as err:
            pass

        urls = driver.find_elements_by_css_selector('div[class="refine-block category"] li a')
        categoryNodes = driver.find_elements_by_css_selector('div[class="refine-block category"] li a span')

        categoryNames = []
        for node in categoryNodes:
            if node.text != '':
                categoryNames.append(node.text)

        self.categories = []

        for name, url in zip(categoryNames, urls):
            element = {
                'name':  name,
                'url': url.get_attribute('href')
            }

            self.categories.append(element)


    def get_sub_category(self, driver):
        categoryNodes = driver.find_elements_by_css_selector('div[class="refine-block category"] li a')
        self.sub_categories = []
        for node in categoryNodes:
            element = {
                'name':  node.text,
                'url': node.get_attribute('href')
            }

            self.sub_categories.append(element)

    def fetch_item_url(self, driver, scrollStep=20):

        scroll_bottom(driver, scrollStep)
        items = driver.find_elements_by_css_selector('a.item-title')
        logger.debug('アイテム数：' + str(len(items)))
        self.itemUrls = []

        for item in items:
            self.itemUrls.append(item.get_attribute('href'))



class Item():

    def __init__(self, url):
        self.url = url
        self.item_info = {
            'title': '',
            'url': url,
            'price': 0
        }

    def fetch_title(self, driver):

        title = driver.find_element_by_css_selector('h1.product-title-text')
        self.item_info['title'] = title.text
        time.sleep(1)


    def fetch_price(self, driver):

        price = driver.find_element_by_css_selector('div[class="product-info"] span[class="product-price-value"]')
        self.item_info['price'] = price.text
        time.sleep(1)

    def fetch_all(self, driver):

        driver.get(self.url)
        self.fetch_title(driver)
        self.fetch_price(driver)

