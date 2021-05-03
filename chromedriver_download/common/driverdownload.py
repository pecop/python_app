# Standard import
import os
import sys
from os.path import join, dirname
import re
import urllib.request
import zipfile


# Third party import
import requests
from bs4 import BeautifulSoup


# Local import
import common.dotenv_settings


# Global
CHROME_DRIVER_DIRECTORY = common.dotenv_settings.CHROME_DRIVER_DIRECTORY
CHROME_DRIVER_URL = 'https://chromedriver.chromium.org/downloads'
CHROME_DRIVER_LINK_PATTERN = 'https://chromedriver.storage.googleapis.com/index.html?path='
CHROME_STORAGE_URL = 'https://chromedriver.storage.googleapis.com/'

if os.name == 'nt':  # Windows
    ZIP_FILE_NAME = 'chromedriver_win32.zip'
elif os.name == 'posix':  # Mac
    ZIP_FILE_NAME = 'chromedriver_mac64.zip'


def get_chrome_version_from_PC():

    files = os.listdir(CHROME_DRIVER_DIRECTORY)
    folders = [file for file in files if os.path.isdir(os.path.join(CHROME_DRIVER_DIRECTORY, file))]

    chrome_version_list = []
    for folder in folders:
        pattern = re.compile('(\d)+(.)+')
        result = pattern.match(folder)
        if result is not None:
            chrome_version_list.append(result.group())

    chrome_version_list.sort(reverse=True)
    latest_version = chrome_version_list[0]

    return latest_version

def delete_micro_version(version):

    version_split = version.split('.')
    version_without_micro = '.'.join(version_split[:3])

    return version_without_micro

def fetch_chrome_match_version(version_without_micro):

    html = requests.get(CHROME_DRIVER_URL)
    soup = BeautifulSoup(html.content, 'lxml')
    linkNodes = soup.select('a')

    links = []
    for node in linkNodes:
        try:
            link = node.attrs['href']
        except KeyError:
            pass

        if CHROME_DRIVER_LINK_PATTERN in link:
            if version_without_micro in link:
                links.append(link)

    links.sort(reverse=True)
    latest_driver_link = links[0]
    pattern = re.compile('(\d)+(.)+')
    match_version = pattern.search(latest_driver_link).group().replace('/', '')

    return match_version

def download_zip(match_version):

    if getattr(sys, 'frozen', False):
        directory_path = os.path.dirname(sys.executable)
    else:
        directory_path = os.getcwd()

    download_path = join(directory_path, ZIP_FILE_NAME)

    urllib.request.urlretrieve(CHROME_STORAGE_URL + match_version + '/' + ZIP_FILE_NAME , download_path)
    with zipfile.ZipFile('chromedriver_win32.zip') as existing_zip:
        existing_zip.extractall(directory_path)


def get_chrome_driver():

    latest_version = get_chrome_version_from_PC()
    version_without_micro = delete_micro_version(latest_version)
    match_version = fetch_chrome_match_version(version_without_micro)
    download_zip(match_version)

    return f'Chrome version of PC: {latest_version}, Download driver version: {match_version}'


def main():

    get_chrome_driver()

if __name__ == '__main__':
    main()