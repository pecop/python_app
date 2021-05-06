import os
import sys
from os.path import join, dirname
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    directory_path = os.path.dirname(sys.executable)
    if '.app' in directory_path:
        idx = directory_path.find('.app') 
        directory_path = directory_path[:idx]
        idx = directory_path.rfind('/')
        directory_path = directory_path[:idx]
else:
    directory_path = os.getcwd()

dotenv_path = join(directory_path, '.env')
load_dotenv(dotenv_path)

CHROME_PROFILE_PATH = os.environ.get('CHROME_PROFILE_PATH')
