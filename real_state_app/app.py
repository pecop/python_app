# %%

# General import
import sys
import time
import pandas as pd
# from logging import getLogger,  FileHandler, StreamHandler, Formatter, DEBUG
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
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    WebDriverException,
    InvalidArgumentException,
)


# Original import
from logger import logger
from scraping import set_driver, get_with_wait, parse_html, parse_html_selenium
import settings


# 不動産ジャパンURL
top_url = 'https://www.fudousan.or.jp'
search_url = 'https://www.fudousan.or.jp/property/buy/13/area/list?m_adr%5B%5D=13101&m_adr%5B%5D=13102&m_adr%5B%5D=13103&m_adr%5B%5D=13104&m_adr%5B%5D=13105&m_adr%5B%5D=13106&m_adr%5B%5D=13107&m_adr%5B%5D=13108&m_adr%5B%5D=13109&m_adr%5B%5D=13110&m_adr%5B%5D=13111&m_adr%5B%5D=13112&m_adr%5B%5D=13113&m_adr%5B%5D=13114&m_adr%5B%5D=13115&m_adr%5B%5D=13116&m_adr%5B%5D=13117&m_adr%5B%5D=13118&m_adr%5B%5D=13119&m_adr%5B%5D=13120&m_adr%5B%5D=13121&m_adr%5B%5D=13122&m_adr%5B%5D=13123&ptm%5B%5D=0103&price_b_from=&price_b_to=&keyword=&eki_walk=&bus_walk=&exclusive_area_from=&exclusive_area_to=&exclusive_area_from=&exclusive_area_to=&built='
page_url_element = '&page='


# オリジナルエラー
class NoEmailPassword(Exception):  # EmailとPasswordが設定されてない
    pass


class NoSelector(Exception):  # セレクタが見つからない
    pass


# マンションレビューログイン情報取得
try:
    EMAIL = settings.EMAIL
    PASSWORD = settings.PASSWORD
    if EMAIL is None or PASSWORD is None:
        raise NoEmailPassword
except NoEmailPassword:
    logger.error('.envファイルを作成し、マンションレビューのログイン情報(emailとpassword)を入力してください。')
    sys.exit()


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

        name = soup.select_one('h1.detail-h1')
        try:
            if name is None:
                raise NoSelector
        except NoSelector:
            logger.error('物件名が見つかりません。セレクタが変更されている可能性があります。')
            sys.exit()  # セレクタが見つからなければ、終了する。
        name = name.get_text(strip=True)

        # スペースや改行などの不要な文字列を削除
        name = name.replace('?', '')

        if name != '':  # 物件名有無の判定
            self.item_info['name'] = name
            self.isName = True
            self.countup()
            logger.debug(f'物件名：{name}')
        else:
            logger.debug('物件名：無し')

    # 価格取得
    def fetch_price(self, soup):

        try:
            price = soup.select_one('div.price').get_text(strip=True)
            # スペースや改行、日本語、カンマなどの不要な文字列を削除
            price = price.replace(':', '').replace('：', '').replace(',', '')
            price = price.replace('万円', '').replace('価格', '').replace('億', '')
            if price != '':
                self.item_info['price'] = int(price)
                logger.debug(f'価格：{price}万円')
            else:
                logger.debug('価格：無し')
        except Exception as err:
            logger.error(err)
            logger.debug('価格：無し')

    # 表から以下の情報を取得
    # 所在地、専有面積、築年月、現況、引渡し時期、備考1
    def fetch_table_info(self, soup):

        table_selector = 'div[class="detail-info"] td[class^="info-val"]'
        table_info_val = soup.select(table_selector)

        try:
            if not table_info_val:
                raise NoSelector
        except NoSelector:
            logger.error('物件詳細情報の表が見つかりません。セレクタが変更されている可能性があります。')
            sys.exit()

        place = table_info_val[3].get_text(strip=True)
        place = place.replace('周辺地図', '')  # 不要文字列削除
        self.item_info['place'] = place

        area = table_info_val[9].get_text(strip=True)
        area = area.replace('㎡', '')  # 不要文字列削除
        area = area.replace('壁芯', '').replace('内法', '')  # 不要文字列削除
        try:
            self.item_info['area'] = float(area)
        except ValueError as err:
            logger.error(err)
            logger.error('専有面積の文字列⇒数値変換に失敗しました。不要文字列を追加するなどしてください。')
            sys.exit()

        age = table_info_val[25]
        age = age.get_text(strip=True)
        self.item_info['age'] = age

        situation = table_info_val[38]
        situation = situation.get_text(strip=True)
        self.item_info['situation'] = situation

        delivery = table_info_val[44]
        delivery = delivery.get_text(strip=True)
        self.item_info['delivery'] = delivery

        remark = table_info_val[49]
        remark = remark.get_text(strip=True)
        self.item_info['remark'] = remark

        logger.debug(f'所在地：{place}, 専有面積：{area}㎡, 築年月：{age}')
        logger.debug(f'現況：{situation}, 引渡し時期：{delivery}, 備考1：{remark}')


def search(driver, page=1):

    url = search_url + page_url_element + str(page)  # ページ設定
    get_with_wait(driver, url, isWait=True)  # 待機付きページ移動

    soup = parse_html_selenium(driver)
    item_nodes = soup.select('a.prop-title-link')  # 各物件のURLが格納されているaタグを取得
    try:
        if not item_nodes:
            raise NoSelector
    except NoSelector:
        logger.error('物件リンク(aタグ)が見つかりません。セレクタが変更されている可能性があります。')
        sys.exit()  # セレクタが見つからなければ、終了する。
    items = []

    for node in item_nodes:

        items.append(Item(top_url + node.attrs['href']))  # 各物件のURL取得

    for i, item in enumerate(items, 1):
        logger.debug(f'No.{i}')
        item.fetch_info(driver)  # 不動産ジャパンの必要情報取得
        logger.debug('')

    return driver, items

# %%


driver = set_driver(isHeadless=False, isManager=True)  # Seleniumドライバ設定

if driver is None:  # ドライバの設定が不正の場合はNoneが返ってくるので、システム終了
    sys.exit()

search(driver)

# %%

# items_list = []
# for i in range(1):
#     driver, items = search(driver, i+1)
#     items_list += items

# %%

# logger.debug(f'アイテム数：{Item.isName_count}/{len(items_list)}')
# for item in items_list:
#     pprint(item.item_info)

# %%

# url = 'https://www.fudousan.or.jp/property/detail?p_no=000004123049'
# # url = 'https://www.fudousan.or.jp/property/detail?p_no=000004134652'
# get_with_wait(driver, url, isWait=True)  # 待機付きページ移動
# soup = parse_html_selenium(driver)

# name = soup.select_one('h1.detail-h1')
# try:
#     if name is None:
#         raise NoSelector
# except NoSelector:
#     sys.exit()  # セレクタが見つからなければ、終了する。
# name = name.get_text(strip=True)

# print(name)

# %%

# %%

# keyword = 'アプレシティ高円寺'
# review_url = f'https://www.mansion-review.jp/search/result/?mname={keyword}&direct_search_mname=1&bunjo_type=0&search=1#result'
# driver = set_driver(isHeadless=False, isManager=True) # Seleniumドライバ設定
# get_with_wait(driver, review_url, isWait=True)

# %%

# from selenium.webdriver.common.action_chains import ActionChains

# wait = WebDriverWait(driver, 10)
# wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.user-icon')))
# driver.find_element_by_css_selector('span.user-icon').click()
# wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[class="login_pop cboxElement"]')))
# driver.find_element_by_css_selector('a[class="login_pop cboxElement"]').click()
# time.sleep(1)
# input_email = driver.find_element_by_css_selector('input.text')
# input_email.send_keys(Keys.CONTROL + 'a')
# input_email.send_keys(Keys.DELETE)
# input_email.send_keys(EMAIL)
# input_password = driver.find_element_by_css_selector('input.password')
# input_password.send_keys(Keys.CONTROL + 'a')
# input_password.send_keys(Keys.DELETE)
# input_password.send_keys(PASSWORD)
# # element = driver.find_element_by_css_selector('input[class="cta_button_input"]')
# # element = driver.find_element_by_css_selector('input[class="cta_button_input search_submit"]')
# element = driver.find_element_by_xpath('//*[@id="loginArea"]/form/table/tbody/tr[3]/td/div/input')
# # element = driver.find_element_by_xpath('/html/body/div[12]/div[1]/div[2]/div[2]/div[1]/div/form/table/tbody/tr[3]/td/div')
# loc = element.location
# x, y = loc['x'], loc['y']
# print(x, y)
# actions = ActionChains(driver)
# actions.move_by_offset(x, y)
# actions.click()
# actions.perform()


# %%

# print(EMAIL, PASSWORD)

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
