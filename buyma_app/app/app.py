# %%
import os
import sys
import signal
from selenium.webdriver import Chrome, ChromeOptions
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from collections import defaultdict
from logging import getLogger,  FileHandler, StreamHandler, Formatter, DEBUG
import threading
from concurrent import futures


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

class Search():

    def __init__(self, url):
        self.url = url
        self.search_url = ''
        self.keyword = ''
        self.isSale = False
        self.cost_range = {'lower': '0', 'upper': '-'}
        self.option = ''
        self.soup = ''
    
    def make_url(self):

        self.set_option()
        self.search_url = self.url + self.keyword + self.option
    
    def set_keyword(self, keyword):

        self.keyword = keyword + '/'
    
    def set_isSale(self, isSale):

        self.isSale = isSale
    
    def set_cost_range(self, lower='0', upper='-'):

        self.cost_range['upper'] = str(upper)
        self.cost_range['lower'] = str(lower)

    def set_option(self):

        if self.cost_range['upper'] != '-':
            self.option = '?' + 'pc=' + self.cost_range['lower'] + '-' + self.cost_range['upper']
        else:
            self.option = '?' + 'pc=' + self.cost_range['lower']

        if self.isSale:
            self.option += '&' + 'rp=' + '1'
        else:
            self.option += '&' + 'rp=' + '0'
    
    def parse_html(self):

        html = requests.get(self.search_url)
        html.encoding = html.apparent_encoding
        self.soup = BeautifulSoup(html.content, "html.parser")

def parse_html(url):

    html = requests.get(url)
    html.encoding = html.apparent_encoding
    soup = BeautifulSoup(html.content, "html.parser")

    return soup

def set_driver(IsHeadless):

    options = ChromeOptions()

    try:
        if os.name == 'nt': #Windows
            driver_path = 'chromedriver.exe'
        elif os.name == 'posix': #Mac
            driver_path = 'chromedriver'
    except Exception as err:
        logger.error(err)
        sys.exit()

    if IsHeadless == True:
        options.add_argument('--headless')

    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')

    driver = Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)
    driver.set_window_size('1200', '1000')

    return driver

def keep_open_driver(driver):

    os.kill(driver.service.process.pid, signal.SIGTERM)

def main():

    url = 'https://www.buyma.com/r/'

    search = Search(url)
    search.set_keyword('who.me.see')
    search.set_isSale(isSale=True)
    search.set_cost_range(upper=100)
    search.make_url()
    search_url = search.search_url
    logger.debug(search_url)
  
    IsHeadless = False
    driver = set_driver(IsHeadless)

    driver.get(url)
    time.sleep(1)
    search.parse_html()
    
    keep_open_driver(driver)
 
if __name__ == "__main__":
    main()

# %%
