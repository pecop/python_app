# 不動産スクレイピングアプリ

<hr>

## 開発環境
- Python: 3.8.2
- pip: requirements.txt

<hr>

## 仕様

#### 対象サイト

- 不動産ジャパン：https://www.fudousan.or.jp
- マンションレビュー：https://www.mansion-review.jp/

#### スクレイピング手法

- 不動産ジャパンは、BeautifulSoup単体だとロボット判定され、1回のスクレイピングで数時間ブロックされてしまうので、クローリング及びhtmlのparseまではSeleniumで実行し、parseした後のデータ抽出をBeautifulSoupにて実行する。
- マンションレビューから抽出したい情報は、ログインしないと表示されないので、Seleniumよりログイン操作を自動で行う。
- 検索数は100件であり、高速化の必要性はないので、並列処理は行わない。

#### スクレイピングフロー

※スクレイピングは3項以降とし、1-2項は事前にマニュアルで実施し、スクレイピング対象のURLを事前に取得しておく。検索条件を変更たい場合は、このURLを変更することで対応可能。

1. 不動産ジャパンTOPに移動し、以下の通り、東京都の物件を探すURLまで移動する。
- TOP(下記画像) -> [不動産物件検索] -> [買う] -> [マンション] -> [東京都] -> [エリアから検索]をクリック
- [エリアから東京都の売買物件(マンション)を探す]に移動

<img src=./img/不動産ジャパン_TOP.png>

<hr>

2. エリアにチェックを入れ、価格上限(3000万円)を入力し、検索する。
- [エリア全てチェック] -> [価格上限3000万円] -> [検索]

<img src=./img/不動産ジャパン_東京都_エリア検索.png>

<hr>

3. 以下のURLに移動するので、このURLからスクレイピングを開始する。ページ指定する場合は、下記URLに`&page={number}`を付与(n: ページ数)する。

- [スクレイピング対象URL](https://www.fudousan.or.jp/property/buy/13/area/list?m_adr%5B%5D=13101&m_adr%5B%5D=13102&m_adr%5B%5D=13103&m_adr%5B%5D=13104&m_adr%5B%5D=13105&m_adr%5B%5D=13106&m_adr%5B%5D=13107&m_adr%5B%5D=13108&m_adr%5B%5D=13109&m_adr%5B%5D=13110&m_adr%5B%5D=13111&m_adr%5B%5D=13112&m_adr%5B%5D=13113&m_adr%5B%5D=13114&m_adr%5B%5D=13115&m_adr%5B%5D=13116&m_adr%5B%5D=13117&m_adr%5B%5D=13118&m_adr%5B%5D=13119&m_adr%5B%5D=13120&m_adr%5B%5D=13121&m_adr%5B%5D=13122&m_adr%5B%5D=13123&m_adr%5B%5D=13201&m_adr%5B%5D=13202&m_adr%5B%5D=13203&m_adr%5B%5D=13204&m_adr%5B%5D=13205&m_adr%5B%5D=13206&m_adr%5B%5D=13207&m_adr%5B%5D=13208&m_adr%5B%5D=13209&m_adr%5B%5D=13210&m_adr%5B%5D=13211&m_adr%5B%5D=13212&m_adr%5B%5D=13213&m_adr%5B%5D=13214&m_adr%5B%5D=13215&m_adr%5B%5D=13218&m_adr%5B%5D=13219&m_adr%5B%5D=13220&m_adr%5B%5D=13221&m_adr%5B%5D=13222&m_adr%5B%5D=13223&m_adr%5B%5D=13224&m_adr%5B%5D=13225&m_adr%5B%5D=13227&m_adr%5B%5D=13228&m_adr%5B%5D=13229&ptm%5B%5D=0103&price_b_from=&price_b_to=30000000&keyword=&eki_walk=&bus_walk=&exclusive_area_from=&exclusive_area_to=&exclusive_area_from=&exclusive_area_to=&built=)


4. 各物件のURLを取得
5. 各物件のURLに移動し、下図の項目を取得する。ただし、建物名(物件名)がないものに関してはスキップ(6項もスキップ)する。

<img src=./img/不動産ジャパン_抽出情報.png>

6. 建物名をキーワードとして、マンションレビューで検索する。下記URLの`{keyword}`の箇所に建物名を入力することで検索可能。初回検索時はログインする(一部の項目がログインしていないと表示されないため)。
- https://www.mansion-review.jp/search/result/?mname={keyword}&direct_search_mname=1&bunjo_type=0&search=1#result


8. 検索した結果、一番上に出てきたURLから下図の項目を取得する。

<img src=./img/マンションレビュー_抽出情報.png>

9.  不動産ジャパンのページ移動し、4-5項を物件が100件になるまで繰り返す。
10. 抽出した情報をエクセル形式(.xlsx)で保存する。ファイル名は`日付_東京都_マンション.xlsx`とする。


## 使用方法

1. 同じバージョンのPythonをインストール
2. 仮想環境を作成(pipenv推奨)
3. 仮想環境起動(pipenv shell)
4. requirements.txtをダウンロードして、仮想環境のルートディレクトリに保存
5. pip install(pipenv install -r ./requirements.txt)
6. .envをルートディレクトリに作成
7. 実行(python app.py)

#### .envフォーマット

ファイル名称は`.env`とし、変更しないこと。

```
EMAIL=XXX.com
PASSWORD=YYY
```
