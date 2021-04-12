import os
import sys
import signal
import requests
from selenium.webdriver import Chrome, ChromeOptions
from bs4 import BeautifulSoup


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

    driver = Chrome(executable_path=os.getcwd() + '/' + driver_path, options=options)
    driver.set_window_size('1200', '1000')

    return driver

def keep_open_driver(driver):

    os.kill(driver.service.process.pid, signal.SIGTERM)


def scroll_bottom(driver, step):

    height = driver.execute_script("return document.body.scrollHeight")
    for x in range(1, height, step):
            driver.execute_script("window.scrollTo(0, "+str(x)+");")


def parse_html(url):

    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'lxml')

    return soup

def parse_html_from_text(text):

    soup = BeautifulSoup(text, 'lxml')

    return soup 