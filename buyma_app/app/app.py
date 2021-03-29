import os
import sys
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
handler = FileHandler('logger.log')
# handler = StreamHandler()
# handler = NullHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
handler.setFormatter(fomatterSetting)
logger.addHandler(handler)
logger.propagate = False

class Job:
    
    def __init__(self, search_basic_url, page):
        self.search_basic_url = search_basic_url
        self.page = page
        firstHalf_url, secondHalf_url = search_basic_url.split('?')
        self.search_url = firstHalf_url + "pg" + str(page) + "/?" + secondHalf_url
        self.soup = ''
        self.job_info = {'name' : [],
                         'apeal': [],
                         'copy' : [],
                         'employment_status': [],
                         'income': [],
                        }
        
    def parse_html(self):

        logger.debug(str(self.page) + "ページ目パース開始")
        html = requests.get(self.search_url)
        html.encoding = html.apparent_encoding
        self.soup = BeautifulSoup(html.content, "html.parser")

    def getJobInfo(self):

        logger.debug(str(self.page) + "ページ目情報取得開始")
        names = self.soup.select('section[class^="cassetteRecruit"]>h3[class$="__name"]')
        copies = self.soup.select('section[class^="cassetteRecruit"]>p[class$="__copy"]')
        infoTables = self.soup.select('div[class^="cassetteRecruit"]>div[class$="__detail"]>div[class*="__main"]')

        for name, copy, infoTable in zip(names, copies, infoTables):

            self.job_info['name'].append(name.text.split('|')[0].replace(' ', '').replace('　', ''))

            try:
                self.job_info['apeal'].append(name.text.split('|')[1].replace(' ', '').replace('　', ''))
            except IndexError as e:
                logger.error("情報がありません")
                self.job_info['apeal'].append('')

            self.job_info['copy'].append(copy.text.split('\n')[1].replace(' ', '').replace('　', ''))
            self.job_info['employment_status'].append(copy.text.split('\n')[2].replace(' ', '').replace('　', ''))

            for content, incom in zip(infoTable.select('.tableCondition__head'), infoTable.select('.tableCondition__body')):

                IsIncom = False
                if '初年度年収' in content.text:
                    self.job_info['income'].append(incom.text)
                    IsIncom = True

            if IsIncom == False:
                self.job_info['income'].append('')

        logger.debug(str(self.page) + "ページ目完了")


def run_getJobInfo(job):

    job.parse_html()
    job.getJobInfo()


def set_driver(driver_path, headless_flg):

    options = ChromeOptions()

    if headless_flg == True:
        options.add_argument('--headless')

    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)


def main():

    search_keyword = input('検索キーワードを入力してください：')
    logger.debug(search_keyword)
    search_url = "https://tenshoku.mynavi.jp/"
    
    # driverを起動
    IsHeadless = True

    try:
        if os.name == 'nt': #Windows
            driver = set_driver("chromedriver.exe", IsHeadless)
        elif os.name == 'posix': #Mac
            driver = set_driver("chromedriver", IsHeadless)
    except Exception as err:
        logger.error(err)
        sys.exit()
    
    driver.set_window_size('1200', '1000')
    driver.get(search_url)
    time.sleep(5)
 
    try:
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
        time.sleep(5)
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
    except:
        pass
  
    # 検索窓に入力
    driver.find_element_by_class_name("topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

    cur_url = driver.current_url
    logger.info(cur_url)

    jobs = []

    # no use multi-thread
    # for i in range(10):

    #     jobs.append(Job(cur_url, i+1))
    #     run_getJobInfo(jobs[i])

    # Multi-thread by threading
    # threads = []
    # for i in range(10):

    #     jobs.append(Job(cur_url, i+1))

    #     t = threading.Thread(name='thread'+str(i+1), target=run_getJobInfo, args=(jobs[i], ))
    #     t.start()
    #     threads.append(t)
    #     time.sleep(1)
  
    # for thread in threads:
    #     thread.join()

    # Multi-thread by concurrent.futures
    with futures.ThreadPoolExecutor(max_workers=10, thread_name_prefix="thread") as executor:
        for i in range(10):
            jobs.append(Job(cur_url, i+1))
            executor.submit(run_getJobInfo, jobs[i])
            time.sleep(1)

    job_info_all = defaultdict(list)
    info_list = jobs[0].job_info.keys()

    for job in jobs:
        for item in info_list:
            job_info_all[item] += job.job_info[item]

    df = pd.DataFrame(job_info_all)
    
    df.to_csv("mynavi_high_incom_list_" + search_keyword + ".csv", encoding='utf-8-sig')

    logger.debug("CSV出力完了")


if __name__ == "__main__":
    main()
