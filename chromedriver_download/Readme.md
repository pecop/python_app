# Chrome Driver自動ダウンロードアプリ

## 目的

Chrome Driverを自動ダウンロードする方法として、`webdriver-manager`を使用する方法があるが、
exeファイルとして、Python環境を持たない人にアプリを配布する場合、`webdriver-manager`を用いてアプリ化しても、
自動ダウンロードは正常に動作しない。
よって、`webdriver-manager`はPython環境でのみしか動作しないため、exeファイル動作させる場合、手動でDriverをダウンロードする必要があった。また、Chromeのバージョンを確認し、同じバージョンをDriverをダウンロードするのは地味に面倒。
この問題を解決するために、自動ダウンロードアプリを作成した。
exeファイルの場合は、ダブルクリックするだけでダウンロードを完了させることができ、pythonファイルの場合は、配布用のアプリに本パッケージを取り込むことで、`WebDriverException`エラーが発生した場合に自動ダウンロードすることができる。


## 開発環境
- Python: 3.8.2
- pip: requirements.txt


## 使用方法

#### exeファイルの場合

**※Macには対応していません！！！**

- `dist`ディレクトリの中に保存されている`driverdownloader.exe`を適当なディレクトリに保存する。
- `driverdownloader.exe`と同じディレクトリに、`.env`ファイルを作成する。
- ブラウザで`chrome://version/`を検索し、Chromeの実行ファイルのパスをコピペする。
- .envを以下の通り編集する。Windowsの場合、`\chrome.exe`は不要。
  
```
CHROME_DRIVER_DIRECTORY=C:\Program Files (x86)\Google\Chrome\Application
```

- `driverdownloader.exe`をダブルクリックすると、DriverとDriverのzipファイルが同じディレクトリに自動保存される。
- コンソールには、PCのChromeのバージョンとダウンロードしたChrome Driverのバージョンが表示される。
- Enterを押すと、コンソールは閉じる。

#### pythonファイルの場合

- 仮想環境構築(3.8.2以降を推奨)
- pipインストール(requirements.txt)
- clone
- `app.py`と同じディレクトリに、`.env`ファイルを作成する。
- ブラウザで`chrome://version/`を検索し、Chromeの実行ファイルのパスをコピペする。
- .envを以下の通り編集する。Windowsの場合、`\chrome.exe`は不要。
  
```
CHROME_DRIVER_DIRECTORY=C:\Program Files (x86)\Google\Chrome\Application
```

- python app.pyを実行。
- コンソールには、PCのChromeのバージョンとダウンロードしたChrome Driverのバージョンが表示される。

## 制作者
- Yoke
