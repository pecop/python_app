from common.driverdownload import get_chrome_driver

version_message = get_chrome_driver()
print(version_message)
input('Enterを押すと終了します。')