from logging import getLogger,  FileHandler, StreamHandler, Formatter, DEBUG


logger = getLogger(__name__)
message = '[%(asctime)s] %(name)s %(threadName)s %(levelname)s: %(message)s'
timeFormatter = '%Y-%m-%d %H:%M:%S'
fomatterSetting = Formatter(message, timeFormatter)
# handler = FileHandler('logger.log')  # テキスト出力する場合はコメントアウトを外す
handler = StreamHandler()  # テキスト出力するときはコメントアウトする
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
handler.setFormatter(fomatterSetting)
logger.addHandler(handler)
logger.propagate = False
