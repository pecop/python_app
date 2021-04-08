import eel
import settings
from app import Search, Item
from scraping import set_driver, parse_html
from datetime import datetime as dt
from logging import getLogger,  FileHandler, StreamHandler, Formatter, DEBUG
import pandas as pd


app_name="web"
end_point="index.html"
size=(850, 850)

IsHeadless = False
driver = None
search = Search('', '')
items = []

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

# @eel.expose
# def searchCategory():
#     category_url = 'https://ja.aliexpress.com/all-wholesale-products.html?spm=a2g0o.category_nav.0.0.300734f6uRXi28'
#     category = Category(category_url)
#     category.search_all()
#     eel.set_category(category.categories)

def error_logger(message, error):

    logger.error(message)
    logger.error(error)
    eel.message(message, True, False)

@eel.expose
def search(keyword):

    global driver
    global search

    try:
        if driver is None:
            driver = set_driver(IsHeadless)
    except Exception as error:
        error_logger('Seleniumドライバ設定エラー', error)
        return None

    try:
        url = 'https://ja.aliexpress.com/all-wholesale-products.html?spm=a2g0o.category_nav.0.0.300734f6uRXi28'
        search = Search(url, keyword)
        search.set_keyword(driver)
        search.set_currency(driver)
        search.get_category(driver)
        eel.message('検索完了、カテゴリを設定しました。絞り込みを必要に応じて設定してください。')
        eel.set_category_info(search.categories)
        eel.view_current_url(driver.current_url)
    except Exception as error:
        error_logger('検索エラー', error)
        return None


@eel.expose
def narrow_category(category_url, isSub=False):

    global driver
    global search

    try:
        driver.get(category_url)
        if not isSub:
            search.get_sub_category(driver)
            eel.message('カテゴリ絞り込み完了、サブカテゴリを設定しました。')
            eel.set_sub_category_info(search.sub_categories)
        else:
            eel.message('サブカテゴリ絞り込み完了')
        eel.view_current_url(driver.current_url)
    except Exception as error:
        error_logger('カテゴリ絞り込みエラー', error)
        return None    


@eel.expose
def narrow_price_range(price_range):

    global driver
    global search

    try:
        search.set_price_range(driver, price_range)
        eel.message('価格範囲絞り込み完了')
        eel.view_current_url(driver.current_url)
    except Exception as error:
        error_logger('価格範囲絞り込みエラー', error)
        return None    


@eel.expose
def fetch():

    global driver
    global search
    global items

    try:
        search.fetch_item_url(driver)
        urls = search.itemUrls
        items = []
        for i in range(5):
            item = Item(urls[i])
            item.fetch_all(driver)
            items.append(item.item_info)
        
        eel.view_item_info(items)
        eel.message('抽出完了')
    except Exception as error:
        error_logger('抽出エラー', error)
        return None    

@eel.expose
def save(fileName):

    titles = []
    prices = []
    urls = []

    for item in items:
        titles.append(item['title'])
        prices.append(item['price'])
        urls.append(item['url'])

    item_dict = {
        'title': titles,
        'price': prices,
        'URL': urls,
    }

    try:
        df = pd.DataFrame(item_dict)
        df.to_csv(dt.now().strftime("%Y%m%d_%H%M") + '_' + fileName + '.csv', encoding='utf-8-sig')
        logger.debug("CSV出力完了")
        eel.message('CSV保存完了')

    except Exception as error:
        error_logger('CSV保存エラー', error) 


def main():
    settings.start(app_name,end_point,size)

if __name__ == "__main__":
    main()

