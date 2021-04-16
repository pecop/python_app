# %%

# General import
import time
import pandas as pd
from logging import getLogger,  FileHandler, StreamHandler, Formatter, DEBUG
from pprint import pprint
from collections import defaultdict
from concurrent import futures

# Scraping import
import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Original import
from scraping import set_driver, get_with_wait, parse_html, parse_html_selenium
import settings

# ロガー設定
logger = getLogger(__name__)
fomatterSetting = Formatter('[%(asctime)s] %(name)s %(threadName)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
# handler = FileHandler('logger.log') # テキスト出力する場合はコメントアウトを外す
handler = StreamHandler() # テキスト出力するときはコメントアウトする
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
handler.setFormatter(fomatterSetting)
logger.addHandler(handler)
logger.propagate = False

# 不動産ジャパンURL
top_url = 'https://www.fudousan.or.jp'
search_url = 'https://www.fudousan.or.jp/property/buy/13/area/list?m_adr%5B%5D=13101&m_adr%5B%5D=13102&m_adr%5B%5D=13103&m_adr%5B%5D=13104&m_adr%5B%5D=13105&m_adr%5B%5D=13106&m_adr%5B%5D=13107&m_adr%5B%5D=13108&m_adr%5B%5D=13109&m_adr%5B%5D=13110&m_adr%5B%5D=13111&m_adr%5B%5D=13112&m_adr%5B%5D=13113&m_adr%5B%5D=13114&m_adr%5B%5D=13115&m_adr%5B%5D=13116&m_adr%5B%5D=13117&m_adr%5B%5D=13118&m_adr%5B%5D=13119&m_adr%5B%5D=13120&m_adr%5B%5D=13121&m_adr%5B%5D=13122&m_adr%5B%5D=13123&ptm%5B%5D=0103&price_b_from=&price_b_to=&keyword=&eki_walk=&bus_walk=&exclusive_area_from=&exclusive_area_to=&exclusive_area_from=&exclusive_area_to=&built='
page_url_element = '&page='

# マンションレビューログイン情報取得

USER_NAME = settings.USER_NAME
PASSWORD = settings.PASSWORD

# 物件クラス
class Item():

    isName_count = 0

    @classmethod
    def countup(cls):
        cls.isName_count += 1
    
    def __init__(self, url):
        self.url = url
        self.isName = False
        self.item_info = {
            'url1': url,
            'url2': '',
            'name': '',
            'price': 0,
            'location': '',
            'area': '',
            'age': '',
            'situation': '',
            'delivery': '',
            'remark': '',
            'estimated_market_price': 0,
            'market_price_divide_price': 0,
            'estimated_yield': 0,
            'unit_price_per_area': 0, 
            'estimated_market_price_per_area': 0,
            'average_rent_per_are': 0,
        }
    
    # 不動産ジャパンから必要情報を抽出
    def fetch_info(self, driver):

        get_with_wait(driver, self.url, isWait=True)
        soup = parse_html_selenium(driver)

        # 物件名取得
        self.fetch_name(soup)

        # 物件名がなければ、スキップ
        if self.isName:
            self.fetch_price(soup)
            self.fetch_table_info(soup)

    # 物件名取得
    def fetch_name(self, soup):

        try:
            name = soup.select_one('h1.detail-h1').get_text(strip=True)
            # スペースや改行などの不要な文字列を削除
            name = name.replace('?', '')
            if name != '': # 物件名有無の判定
                self.item_info['name'] = name
                self.isName = True
                self.countup()
                logger.debug(f'物件名：{name}')
            else:
                logger.debug('物件名：無し')
        except Exception as err:
            logger.debug('物件名：無し')

    # 価格取得
    def fetch_price(self, soup):

        try:
            price = soup.select_one('div.price').get_text(strip=True)
            # スペースや改行、日本語、カンマなどの不要な文字列を削除
            price = price.replace(':', '').replace('：', '').replace(',', '').replace('万円', '').replace('価格', '').replace('億', '')
            if price != '':
                self.item_info['price'] = int(price)
                logger.debug(f'価格：{price}万円')
            else:
                logger.debug('価格：無し')
        except Exception as err:
            logger.debug('価格：無し')

    # 表から以下の情報を取得
    # 所在地、専有面積、築年月、現況、引渡し時期、備考1
    def fetch_table_info(self, soup):

        try:
            # table_info_label = soup.select('div[class="detail-info"] td[class^="info-label"]')
            table_info_val = soup.select('div[class="detail-info"] td[class^="info-val"]')
            place = self.item_info['place'] = (table_info_val[3].get_text(strip=True)).replace('周辺地図', '') # 不要文字列削除
            area = self.item_info['area'] = float((table_info_val[9].get_text(strip=True)).replace('㎡', '').replace('壁芯', '')) # 不要文字列削除
            age = self.item_info['age'] = table_info_val[25].get_text(strip=True)
            situation = self.item_info['situation'] = table_info_val[38].get_text(strip=True)
            delivery = self.item_info['delivery'] = table_info_val[44].get_text(strip=True)
            remark = self.item_info['remark'] = table_info_val[49].get_text(strip=True)

            logger.debug(f'所在地：{place}, 専有面積：{area}, 築年月：{age}')
            logger.debug(f'現況：{situation}, 引渡し時期：{delivery}, 備考1：{remark}')
        except Exception as err:
            logger.debug('詳細情報：無し')


def search(driver, page=1):

    url = search_url + page_url_element + str(page) # ページ設定
    get_with_wait(driver, url, isWait=True) # 待機付きページ移動

    soup = parse_html_selenium(driver)
    item_nodes = soup.select('a.prop-title-link') # 各物件のURLが格納されているaタグを取得
    items = []

    for node in item_nodes:

        items.append(Item(top_url + node.attrs['href'])) # 各物件のURL取得

    for i, item in enumerate(items, 1):
        logger.debug(f'No.{i}')
        item.fetch_info(driver) # 不動産ジャパンの必要情報取得
        logger.debug('')

    return driver, items

# %%

driver = set_driver(isHeadless=False, isManager=True) # Seleniumドライバ設定
items_list = []
for i in range(1):
    driver, items = search(driver, i+1)
    items_list += items

# %%

logger.debug(f'アイテム数：{Item.isName_count}/{len(items_list)}')

# %%

# %%

for item in items_list:
    pprint(item.item_info)

# %%

keyword = 'アプレシティ高円寺'
review_url = f'https://www.mansion-review.jp/search/result/?mname={keyword}&direct_search_mname=1&bunjo_type=0&search=1#result'
driver = set_driver(isHeadless=False, isManager=True) # Seleniumドライバ設定
get_with_wait(driver, review_url, isWait=True)


# %%

print(USER_NAME, PASSWORD)

# %%

# drivers = []

# for i in range(3):
#     driver = driver = set_driver()
#     get_with_wait(driver, 'https://www.fudousan.or.jp', isWait=True)
#     drivers.append(driver)


# %%

# driver = set_driver()
# get_with_wait(driver, search_url, isWait=True)

# %%


# soup = parse_html_selenium(driver)
# item_nodes = soup.select('a.prop-title-link')
# items = []

# for node in item_nodes:

#     items.append(Item(top_url + node.attrs['href']))

# for i, item in enumerate(items, 1):
#     logger.debug(f'No.{i}')
#     item.fetch_info(driver)
#     logger.debug('\n')


# %%

