import os
import sys
from os.path import join, dirname
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    directory_path = os.path.dirname(os.path.abspath(sys.executable))
else:
    directory_path = os.path.dirname(os.path.abspath(__file__))

dotenv_path = join(directory_path, '.env')
load_dotenv(dotenv_path)

CHROME_PROFILE_PATH = os.environ.get('CHROME_PROFILE_PATH')
