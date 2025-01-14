from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
import undetected_chromedriver as uc

ua = UserAgent()
options = webdriver.ChromeOptions()
options.add_argument(f'user-agent={ua.random}')
driver = uc.Chrome(options=options)

DoorDash3 ="https://www.doordash.com/store/mcdonald's-fort-greene-837684/1198057/?event_type=autocomplete&pickup=false"

driver.get(DoorDash3)

x = 0
l = 220

divs = []

while True:
    x+=1

    driver.execute_script('scrollBy(0,30)')
    page = BeautifulSoup(driver.page_source, 'lxml')
    results = page.findAll(class_='Text-sc-1nm69d8-0 flyptG')
    divs.extend(results)
    print(f'{x} of {l} done.')
    if x == l:
        break

for items in divs:
    category_name = items.contents
    print(category_name)