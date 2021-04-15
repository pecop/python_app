import os
import sys
import signal
import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Seleniumドライバ設定
def set_driver(isHeadless=False):

    options = ChromeOptions()

    try:
        if os.name == 'nt': #Windows
            driver_path = 'chromedriver.exe'
        elif os.name == 'posix': #Mac
            driver_path = 'chromedriver'
    except Exception as err:
        logger.error(err)
        sys.exit()

    if isHeadless:
        options.add_argument('--headless')

    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')

    driver = Chrome(executable_path=os.getcwd() + '/' + driver_path, options=options)
    driver.set_window_size('1200', '1000')

    return driver

# ドライバによるページ移動＋ページの全要素がDOM上に現れ, かつheight・widthが0以上になるまで待機
def get_with_wait(driver, url, isWait=False, timeout=10):

    driver.get(url)

    if isWait:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.visibility_of_all_elements_located)

# ドライバを開いたままにする設定
def keep_open_driver(driver):

    os.kill(driver.service.process.pid, signal.SIGTERM)

# サイトがJavaScriptによる表示をしており、画面表示していなければ、要素を取得できない場合、最下部までスクロール
def scroll_bottom(driver, step):

    height = driver.execute_script("return document.body.scrollHeight")
    for x in range(1, height, step):
            driver.execute_script("window.scrollTo(0, "+str(x)+");")

# requestsによるhtmlのparse(ロボット判定されやすいので要注意)
def parse_html(url):

    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'lxml')

    return soup

# Seleniumによるhtmlのparse
def parse_html_selenium(driver):

    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'lxml')

    return soup 