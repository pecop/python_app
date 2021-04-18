# %%
# General import
import sys
import time
import re
import pandas as pd
import numpy as np
from datetime import datetime as dt

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
    NoSuchElementException,
    TimeoutException,
)


# Original import
from logger import logger
from scraping import set_driver, get_with_wait, parse_html, parse_html_selenium
import settings
from spreadsheet_settings import (
    contain_index_header,
    excel_save,
    set_font,
    set_border,
)

# Development import
from pprint import pprint


# 不動産ジャパンURL
top_url = 'https://www.fudousan.or.jp'
search_url = 'https://www.fudousan.or.jp/property/buy/13/area/list?m_adr%5B%5D=13101&m_adr%5B%5D=13102&m_adr%5B%5D=13103&m_adr%5B%5D=13104&m_adr%5B%5D=13105&m_adr%5B%5D=13106&m_adr%5B%5D=13107&m_adr%5B%5D=13108&m_adr%5B%5D=13109&m_adr%5B%5D=13110&m_adr%5B%5D=13111&m_adr%5B%5D=13112&m_adr%5B%5D=13113&m_adr%5B%5D=13114&m_adr%5B%5D=13115&m_adr%5B%5D=13116&m_adr%5B%5D=13117&m_adr%5B%5D=13118&m_adr%5B%5D=13119&m_adr%5B%5D=13120&m_adr%5B%5D=13121&m_adr%5B%5D=13122&m_adr%5B%5D=13123&ptm%5B%5D=0103&price_b_from=&price_b_to=&keyword=&eki_walk=&bus_walk=&exclusive_area_from=&exclusive_area_to=&exclusive_area_from=&exclusive_area_to=&built='
page_url_element = '&page='


# オリジナルエラー
class NoEmailPassword(Exception):  # EmailとPasswordが設定されてない
    pass


class NoSelector(Exception):  # セレクタが見つからない
    pass


class CannotLogin(Exception):  # ログインできない
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
            'average_rent_per_area': 0,
        }

    # 必要情報を抽出
    def fetch_info(self, driver):

        # 不動産ジャパンから必要情報を抽出
        get_with_wait(driver, self.url, isWait=True)
        soup = parse_html_selenium(driver)

        # 物件名取得
        self.fetch_name(soup)

        # 物件名がなければ、スキップ
        if self.isName:
            self.fetch_price(soup)
            self.fetch_table_info(soup)

            # マンションレビューから必要情報を抽出
            self.fetch_mansion_review_info(driver)
            self.calc_price()

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


        price = soup.select_one('div.price')

        try:
            if price is None:
                raise NoSelector
        except NoSelector:
            logger.error('価格が見つかりません。セレクタが変更されている可能性があります。')
            sys.exit()  # セレクタが見つからなければ、終了する。

        price = price.get_text(strip=True)
        pattern = '(\d+億)*(\d,)*(\d)+万円'
        price = re.search(pattern, price).group()
        price = price.replace('万円', '').replace('億', '').replace(',', '')

        try:
            self.item_info['price'] = int(price)
            logger.debug(f'価格：{price}万円')
        except ValueError as err:
            logger.error(err)
            logger.error('数値変換に失敗しました。不要文字が含まれている可能性があります。')
            sys.exit()

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

        location = table_info_val[3].get_text(strip=True)
        location = location.replace('周辺地図', '')  # 不要文字列削除
        self.item_info['location'] = location

        area = table_info_val[9].get_text(strip=True)
        pattern = '\d+.?\d*㎡'
        area = re.search(pattern, area).group()
        area = area.replace('㎡', '')  # 不要文字列削除

        try:
            self.item_info['area'] = float(area)
        except ValueError as err:
            logger.error(err)
            logger.error('数値変換に失敗しました。不要文字が含まれている可能性があります。')
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

        logger.debug(f'所在地：{location}, 専有面積：{area}㎡, 築年月：{age}')
        logger.debug(f'現況：{situation}, 引渡し時期：{delivery}, 備考1：{remark}')
    
    # マンションレビューに移動し情報を抽出(ログイン含む)
    def fetch_mansion_review_info(self, driver):

        keyword = self.item_info['name']
        review_url = f'https://www.mansion-review.jp/search/result/?mname={keyword}&direct_search_mname=1&bunjo_type=0&search=1#result'
        get_with_wait(driver, review_url, isWait=True)
        self.check_login(driver)

        soup = parse_html_selenium(driver)
        estimated_price = soup.select_one('p.tanka span.js_automatic_assessment_sale_nominal_meter_tanka')

        if estimated_price is not None:

            estimated_price = estimated_price.get_text(strip=True)
            estimated_price = estimated_price.replace(',', '')

            try:
                self.item_info['estimated_market_price_per_area'] = int(estimated_price)
                logger.debug(f'推定相場㎡単価：{estimated_price}万円/㎡')
            except ValueError as err:
                logger.error(err)
                logger.error('数値変換に失敗しました。不要文字が含まれている可能性があります。')
                sys.exit()

        else:
            logger.error('推定相場㎡単価が見つかりません。セレクタが変更されている可能性があります。')

        average_list = soup.select('table.mansionOrderContentList tbody.average td')

        if average_list:
            average_rent = average_list[3]
            average_rent = average_rent.get_text(strip=True)
            pattern = '(\d)*,?(\d)+円'
            average_rent = re.search(pattern, average_rent).group()
            average_rent = average_rent.replace('円', "").replace(',', "")

            try:
                self.item_info['average_rent_per_area'] = int(average_rent)
                logger.debug(f'賃料平均㎡単価：{average_rent}円')
            except ValueError as err:
                logger.error(err)
                logger.error('数値変換に失敗しました。不要文字が含まれている可能性があります。')
                sys.exit()

        else:
            logger.error('賃料平均㎡単価が見つかりません。セレクタが変更されている可能性があります。')


    # マンションレビューログインチェック
    def check_login(self, driver):

        soup = parse_html_selenium(driver)
        login_status = soup.select_one('span.user-text')
        login_status = login_status.get_text(strip=True)

        if login_status != 'ログイン中':
            try:
                driver.find_element_by_css_selector('span.user-icon').click()
                wait = WebDriverWait(driver, timeout=10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[class="login_pop cboxElement"]')))
                driver.find_element_by_css_selector('a[class="login_pop cboxElement"]').click()
                time.sleep(1)  # waitで待機すると、入力できないので、sleepを使用
                input_email = driver.find_element_by_css_selector('input.text')
                input_email.send_keys(Keys.CONTROL + 'a')
                input_email.send_keys(Keys.DELETE)
                input_email.send_keys(EMAIL)
                input_password = driver.find_element_by_css_selector('input.password')
                input_password.send_keys(Keys.CONTROL + 'a')
                input_password.send_keys(Keys.DELETE)
                input_password.send_keys(PASSWORD)
                driver.find_element_by_css_selector('input[name="login"]').click()
            except (NoSuchElementException, TimeoutException) as err:
                logger.error(err)
                logger.error('ログインのセレクタが見つかりません。セレクタが変更されている可能性があります。')
                sys.exit()


        wait = WebDriverWait(driver, timeout=30)
        wait.until(EC.visibility_of_all_elements_located)
        soup = parse_html_selenium(driver)
        login_status = soup.select_one('span.user-text')
        login_status = login_status.get_text(strip=True)

        if login_status == 'ログイン中':
            logger.debug('ログイン成功')
        else:
            try:
                raise CannotLogin
            except CannotLogin:
                logger.error('ログインに失敗しました。emailとpasswordを見直してください。')
                sys.exit()

        hasLink = True
        review_links = soup.select('h3[class="title"] a')
        
        if not review_links:
            hasLink = False
            logger.debug('マンションレビューに該当物件がありませんでした。')

        if hasLink:
            review_link = review_links[0].attrs['href']
            self.item_info['url2'] = review_link
            get_with_wait(driver, review_link, isWait=True)
    
    # 価格関連の計算
    def calc_price(self):

        estimated_market_price_per_area = self.item_info['estimated_market_price_per_area']
        average_rent_per_area = self.item_info['average_rent_per_area']
        area = self.item_info['area']
        price = self.item_info['price']

        estimated_market_price = estimated_market_price_per_area * area
        self.item_info['estimated_market_price'] = estimated_market_price
        self.item_info['market_price_divide_price'] = estimated_market_price / price * 100
        self.item_info['estimated_yield'] = (average_rent_per_area * area) / (price * 10000) * 100
        self.item_info['unit_price_per_area'] = price / area


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

        # デバッグ用
        # if i > 3:
        #     break

    return driver, items

def save(items):

    # ファイル名設定
    filename = dt.now().strftime("%Y%m%d_%H%M") + '_東京都_マンション' + '.xlsx'

    url1_list = []
    url2_list = []
    name_list = []
    price_list = []
    location_list = []
    area_list = []
    age_list = []
    situation_list = []
    delivery_list = []
    remark_list = []
    estimated_market_price_list = []
    market_price_divide_price_list = []
    estimated_yield_list = []
    unit_price_per_area_list = []
    estimated_market_price_per_area_list = []
    average_rent_per_area_list = []

    # 物件をクラスから取り出し各要素をリストに変換
    for item in items:
        url1_list.append(item.item_info['url1'])
        url2_list.append(item.item_info['url2'])
        name_list.append(item.item_info['name'])
        price_list.append(item.item_info['price'])
        location_list.append(item.item_info['location'])
        area_list.append(item.item_info['area'])
        age_list.append(item.item_info['age'])
        situation_list.append(item.item_info['situation'])
        delivery_list.append(item.item_info['delivery'])
        remark_list.append(item.item_info['remark'])
        estimated_market_price_list.append(item.item_info['estimated_market_price'])
        market_price_divide_price_list.append(item.item_info['market_price_divide_price'])
        estimated_yield_list.append(item.item_info['estimated_yield'])
        unit_price_per_area_list.append(item.item_info['unit_price_per_area'])
        estimated_market_price_per_area_list.append(item.item_info['estimated_market_price_per_area'])
        average_rent_per_area_list.append(item.item_info['average_rent_per_area'])

    # 各要素ををディクショナリに格納
    item_dict = {
        '価格': price_list,
        '推定相場価格': estimated_market_price_list,
        '相場価格/価格': market_price_divide_price_list,
        '推定利回り': estimated_yield_list,
        '建物名': name_list,
        '所在地': location_list,
        '専有面積': area_list,
        '㎡単価': unit_price_per_area_list,
        '推定相場㎡単価': estimated_market_price_per_area_list,
        '賃料平均㎡単価': average_rent_per_area_list,
        '築年月': age_list,
        '現況': situation_list,
        '引渡し時期': delivery_list,
        '備考1': remark_list,
        '物件詳細URL【不動産ジャパン】': url1_list,
        '物件詳細URL【マンションレビュー】': url2_list,
    }

    df = pd.DataFrame(item_dict)  # ディクショナリをDataFrameに変換
    excel_save(df, filename)  # Excelファイル保存
    set_font(filename)  # フォントをメイリオに設定
    set_border(filename)  # ボーダー追加


def main():
    search_page = 1 # デバッグ用
    driver = set_driver(isHeadless=False, isManager=True)  # Seleniumドライバ設定

    if driver is None:  # ドライバの設定が不正の場合はNoneが返ってくるので、システム終了
        sys.exit()

    items_list = []
    for i in range(search_page):
        driver, items = search(driver, i+1)
        items_list += items

    logger.debug(f'アイテム数：{Item.isName_count}/{len(items_list)}')

    # デバッグ用
    # for item in items_list:
    #     pprint(item.item_info)

    save(items_list)
    driver.quit()  # ドライバ終了

if __name__ == "__main__":
    main()

# %%
