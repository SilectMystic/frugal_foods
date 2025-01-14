from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from fake_useragent import UserAgent
import time
import random
from selenium.webdriver.chrome.options import Options
import pymysql
import pymysql.cursors
import undetected_chromedriver as uc
from dynaconf import Dynaconf
settings = Dynaconf(
    settings_file = ('../settings.toml')
)

ua = UserAgent() 
options = webdriver.ChromeOptions()
options.add_argument(f'user-agent={ua.random}')
driver = uc.Chrome(options=options)
url = 'https://www.whatismybrowser.com/'
driver.get(url)
time.sleep(15)
driver.quit