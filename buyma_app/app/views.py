import eel
import settings
from app import Search, Item
from scraping import set_driver
from datetime import datetime as dt
from logging import getLogger,  FileHandler, StreamHandler, Formatter, DEBUG
import pandas as pd


app_name="web"
end_point="index.html"
size=(800, 750)

url = 'https://www.buyma.com/r/'
search_goods = Search(url)
item = Item('')
IsHeadless = False
driver = None

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

def error_logger(message, error):

    logger.error(message)
    logger.error(error)
    eel.message(message, True)

@eel.expose
def search(searchInfo):

    global driver

    try:
        if driver is None:
            driver = set_driver(IsHeadless)
            eel.message('Selenium driver setting success')
    except Exception as error:
        error_logger('Selenium driver error', error)
        return None

    try:
        logger.debug(searchInfo)
        search_goods.set_basic_info(searchInfo)
        search_url = search_goods.search_url
        logger.debug(search_url)
        driver.get(search_url)
        eel.message('Search success')
        eel.fetch_enable()

    except Exception as error:
        error_logger('Search error', error)


@eel.expose
def fetch(fetchNumber):

    global item

    try:
        current_url = driver.current_url
        logger.debug(current_url)
        search_goods.parse_html()
        soup = search_goods.soup

        item = Item(search_goods.url[:-2])
        item.analyze_soup(soup)
        logger.debug(item.url)
        item.fetch_info(fetchNumber)
        eel.message('Fetch sucess')
        eel.viewInfo(item.item_info)
        eel.save_enable()

    except Exception as error:
        error_logger('Fetch error', error) 

@eel.expose
def save(fileName):

    try:
        df = pd.DataFrame(item.item_info)
        df.to_csv(dt.now().strftime("%Y%m%d_%H%M") + '_' + fileName + '_' + '.csv', encoding='utf-8-sig')
        logger.debug("CSV出力完了")
        eel.message('Save sucess')

    except Exception as error:
        error_logger('Save error', error) 

def main():
    settings.start(app_name,end_point,size)

if __name__ == "__main__":
    main()

