# Standard import
import os
import sys
from os.path import join, dirname
from datetime import datetime as dt


# Third party import
import eel
import pandas as pd


# Original import
import settings
from app import (
    Item,
    CHROME_PROFILE_PATH,
    TOP_URL,
)
from my_package.logger import logger
from my_package.scraping import (
    set_driver,
    get_with_wait,
    parse_html,
    parse_html_selenium,
    keep_open_driver
)
from my_package.spreadsheet_settings import (
    excel_save,
    set_font,
    set_border,
)


# Global
app_name = 'web'
end_point = 'index.html'
size = (800, 750)
items = []
driver = None


# Python function
def front_logger(message):

    now = dt.now().strftime('%m/%d %H:%M:%S： ')
    logger.debug(message)
    eel.logger(now + message)


# Python function from JavaScript
@eel.expose
def search():

    front_logger('検索中・・・')

    url = 'https://www.mercari.com/jp/search/?sort_order=&keyword=%E3%83%8A%E3%82%A4%E3%82%AD&category_root=2&category_child=&brand_name=&brand_id=&size_group=&price_min=3000&price_max=5000&item_condition_id%5B1%5D=1&status_trading_sold_out=1'

    driver = set_driver(isHeadless=False, isManager=False, isExtension=True, profile_path=CHROME_PROFILE_PATH)  # Seleniumドライバ設定

    if driver is None:  # ドライバの設定が不正の場合はNoneが返ってくるので、システム終了
        sys.exit()

    get_with_wait(driver, url, isWait=True)  # 待機付きページ移動
    soup = parse_html_selenium(driver)

    links = []
    link_nodes = soup.select('section.items-box a')

    for node in link_nodes:
        links.append(TOP_URL + node.attrs['href'])

    items = []

    start = dt.now().strftime('%Y%m%d_%H%M%S')

    for link in links:
        logger.debug(f'No.{Item.count + 1}')
        item = Item(link)
        items.append(item)
        item.fetch_info(driver)
        logger.debug('')

        break

    end = dt.now().strftime('%Y%m%d_%H%M%S')
    logger.debug(f'開始時間：{start}, 終了時間：{end}')

    # ファイル名設定
    filename = dt.now().strftime('%Y%m%d_%H%M') + '_mercari_demo' + '.xlsx'
    if getattr(sys, 'frozen', False):
        directory_path = os.path.dirname(sys.executable)
    else:
        directory_path = os.getcwd()
    file_path = join(directory_path, filename)

    keys = items[0].item_info  # 取得情報のキー取得

    # 各取得情報の空リスト作成
    values = []
    for i in range(len(keys)):
        values.append([])
    item_dict = dict(zip(keys, values))

    # Itemの情報を辞書内のリストに追加
    for item in items:
        for k, v in item.item_info.items():
                item_dict[k].append(v)

    df = pd.DataFrame(item_dict)  # ディクショナリをDataFrameに変換
    df.index += 1  # indexを1始まりに設定
    excel_save(df, file_path)  # Excelファイル保存
    set_font(file_path)  # フォントをメイリオに設定
    set_border(file_path)  # ボーダー追加


    return 'Success'

def main():
    settings.start(app_name,end_point,size)

if __name__ == '__main__':
    main()

