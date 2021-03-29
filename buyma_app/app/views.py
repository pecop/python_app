import eel
import settings
import app
from logging import getLogger,  FileHandler, StreamHandler, Formatter, DEBUG


app_name="web"
end_point="index.html"
size=(750, 750)

url = 'https://www.buyma.com/r/'
search = Search(url)

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




def main():
    settings.start(app_name,end_point,size)

if __name__ == "__main__":
    main()

