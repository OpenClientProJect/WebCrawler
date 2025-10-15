import os
from dotenv import load_dotenv

load_dotenv(r'C:\Users\Administrator\PycharmProjects\PythonProject\threadsold\example.env')

DEBUG = os.getenv('DEBUG')
ACCOUNT_USERNAME = os.getenv('ACCOUNT_USERNAME')
ACCOUNT_PASSWORD = os.getenv('ACCOUNT_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY'))
REQUEST_PROXY = os.getenv('REQUEST_PROXY')
