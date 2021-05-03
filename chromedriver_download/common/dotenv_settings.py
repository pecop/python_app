import os
import sys
from os.path import join, dirname
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    directory_path = os.path.dirname(sys.executable)
else:
    directory_path = os.getcwd()
dotenv_path = join(directory_path, '.env')
load_dotenv(dotenv_path)

CHROME_DRIVER_DIRECTORY = os.environ.get('CHROME_DRIVER_DIRECTORY')
