import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from collections import defaultdict
from logging import getLogger,  FileHandler, StreamHandler, Formatter, DEBUG
import threading
from concurrent import futures
from scraping import parse_html


logger = getLogger(__name__)
fomatterSetting = Formatter('[%(asctime)s] %(name)s %(threadName)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
handler = FileHandler('logger.log')
# handler = StreamHandler()
# handler = NullHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
handler.setFormatter(fomatterSetting)
logger.addHandler(handler)
logger.propagate = False

class Search():

    def __init__(self, url):
        self.url = url
        self.search_url = ''
        self.keyword = ''
        self.isSale = False
        self.price_range = {'lower': '0', 'upper': '-'}
        self.option = ''
        self.soup = ''
    
    def make_url(self):

        self.set_option()
        self.search_url = self.url + self.keyword + self.option
    
    def set_keyword(self, keyword):

        self.keyword = keyword + '/'
    
    def set_isSale(self, isSale):

        self.isSale = isSale
    
    def set_price_range(self, lower='0', upper='-'):

        if lower == '':
            self.price_range['lower'] = '0'
        else:
            self.price_range['lower'] = str(lower)

        if upper == '':
            self.price_range['upper'] = '-'
        else:
            self.price_range['upper'] = str(upper)
        
    def set_option(self):

        if self.price_range['upper'] != '-':
            self.option = '?' + 'pc=' + self.price_range['lower'] + '-' + self.price_range['upper']
        else:
            self.option = '?' + 'pc=' + self.price_range['lower']

        if self.isSale:
            self.option += '&' + 'rp=' + '1'
        else:
            self.option += '&' + 'rp=' + '0'

    def set_basic_info(self, searchInfo):

        self.set_keyword(searchInfo['keyword'])
        self.set_isSale(searchInfo['isSale'])
        self.set_price_range(searchInfo['priceLower'], searchInfo['priceUpper'])
        self.set_option()
        self.make_url()
    
    def parse_html(self, current_url=''):
        
        if current_url == '':
            self.soup = parse_html(self.search_url)
        else:
            self.soup = parse_html(current_url)


class Item():

    def __init__(self, url):
        self.url = url
        self.items = []
        self.item_info = {
            'name': [],
            'price': [],
            'access': [],
            'like': [],
            'category1': [],
            'category2': [],
            'category3': [],
        }

    def analyze_soup(self, soup):

        links = soup.select('div[class="product_name"]>a[class="js-track-search-action js-ecommerce-item-click"]')
        logger.debug(len(links))

        for link in links:
            self.items.append(link.get('href'))


    def fetch_info(self, number):

        for i, item in enumerate(self.items):
            if i > number-1:
                break
            
            soup = parse_html(self.url + item)
            self.select_all(soup)
            time.sleep(1)
            logger.debug(str(i+1) + '件目完了')
        

    def select_name(self, soup):

        self.item_info['name'].append(soup.select_one('#item_h1>span').text)

    def select_price(self, soup):

        text = soup.select_one('span[class="price_txt"]').text
        text = text[1:]
        text = text.replace(',', '')
        self.item_info['price'].append(int(text))

    def select_access(self, soup):

        text = soup.select_one('span[class="ac_count"]').text
        text = text.replace(',', '')
        self.item_info['access'].append(int(text))

    def select_like(self, soup):

        text = soup.select_one('span[class="fav_count"]').text
        text = text[:-1]
        text = text.replace(',', '')
        self.item_info['like'].append(int(text))
    
    def select_category(self, soup):

        categories = soup.select('#s_cate a[class="ulinelink"]')
        for i, category in enumerate(categories):
            self.item_info['category' + str(i+1)].append(category.text)

    def select_all(self, soup):

        self.select_name(soup)
        self.select_price(soup)
        self.select_access(soup)
        self.select_like(soup)
        self.select_category(soup)

