from common.driverdownload import get_chrome_driver

def main():

    version_message = get_chrome_driver()
    print(version_message)
    input('Enterを押すと終了します。')

if __name__ == '__main__':
    main()