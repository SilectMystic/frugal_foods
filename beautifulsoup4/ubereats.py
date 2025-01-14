from bs4 import BeautifulSoup
import requests
from selenium import webdriver
# from fake_useragent import UserAgent
import time
import random
from selenium.webdriver.chrome.options import Options
import pymysql
import pymysql.cursors

#These are links to try and scan all going to the same McDonald's
DoorDash = "https://www.doordash.com/store/mcdonald's-southside-837652/?cursor=eyJzZWFyY2hfaXRlbV9jYXJvdXNlbF9jdXJzb3IiOnsicXVlcnkiOiJtYyBkb24iLCJpdGVtX2lkcyI6W10sInNlYXJjaF90ZXJtIjoibWMgZG9uIiwidmVydGljYWxfaWQiOi05OTksInZlcnRpY2FsX25hbWUiOiJhbGwifSwic3RvcmVfcHJpbWFyeV92ZXJ0aWNhbF9pZHMiOlsxLDE5Nl19&pickup=false"
FrugalFoods='https://frugal-foods.circuitbreakers.tech/restaurant/7'
GrubHub='https://www.grubhub.com/restaurant/mcdonalds-267-broadway-brooklyn/1339391'
UberEats = "https://www.ubereats.com/store/two-hands-williamsburg/nQGYFCLJR8OjZge6PpNCwQ?diningMode=DELIVERY&sc=SEARCH_SUGGESTION"
UberEats2 = "https://www.ubereats.com/store/mcdonalds-brooklyn-flatbush-ave/mAWk-EcAQ3GYjO2AIcKMrw/c21cd42b-7f1e-5201-af9c-ce9eac19f919?diningMode=DELIVERY&ps=1"
UberEats3 = "https://www.ubereats.com/store/mcdonalds-brooklyn-flatbush-ave/mAWk-EcAQ3GYjO2AIcKMrw/fd23bf60-99af-5aa0-bd62-04126eb10e5c?diningMode=DELIVERY&ps=1"
Postmates="https://postmates.com/store/mcdonalds-brooklyn-flatbush-ave/mAWk-EcAQ3GYjO2AIcKMrw?diningMode=DELIVERY"
# result = requests.get(url).text

# Dont delete commented code here since this was done to try and fool the anti-bot at grubhub.
# options = Options()
# ua = UserAgent()
# user_agent = ua.random
# print(user_agent)
# options.add_argument(f'--user-agent={user_agent}')
# driver = webdriver.Chrome(options=options)

# Driver is from a module called Selenium that you are going to need to install (pip3 install selenium). Selenium is used to have beautifulsoup4
# read javascript because if you do it normally it won't work.

# This code is to tell the webdriver from selenium what browser to use. For example its using Chrome.
driver = webdriver.Chrome()
# driver.get is to tell the webdriver to what website to search and scan.
driver.get(UberEats)

# x and l are variables used in order to control the while loop statement thats used below, for example l its used as the limit of iterations
# while x counts the amounts of iterations.(Right now its on 50 for testing purposes. Recommend to put it on 600 for an actual scan).
x = 0
l = 500

# The variable divs its being used to store all the data that is gathered by beautifulsoup4 in order to use later in an for loop.
divs = []

while True:
    x += 1
    # driver.execute is being used here to scroll very slowly through the website and heavly recommend to leave it at 30 since the data on
    # the websites clear very fast while scrolling and 30 seems to be catching everything so far.
    driver.execute_script('scrollBy(0,30)')
    # page variable is just telling beautifulsoup4 where to read the website and also the encoder.
    page = BeautifulSoup(driver.page_source, 'lxml')
    # In the results variable is set to save the page.findAll expression which what it does is that it searches the page variable based on
    # the requirements that you give it, for example here the requirements is that the tag must be a div and the data anchor id to be
    # MenuItem. findAll what it does is that it searches the entire document while find only searches for the first one.
    results = page.findAll(class_="al am cj ae ak eu")
    # .extend saves all input to the divs variable from before the while loop.
    divs.extend(results)
    print(f'{x} of {l} done.')

    # this segment of code here is to print the content in a html file for testing purposes.
    # with open('ue.html', 'w', encoding='utf-8') as f:
    #     f.write(str(results))
    # n = random.randint(0,50)
    # if n == 5:
    #     print('Time to sleep')
    #     time.sleep(2)
    
    # This can most likely be ignored since its just to increase the limit on the l variable by 200 iterations if you are running different pages.
    # if x == l:
    #     j = input('Do you want to add more? (Y/N)')
    #     if j == 'Y':
    #         l+=200
    #     else:
    #         break

    if x == l:
        break

# db_link is just for the connection and a print statement so please just change it here.
db_link = '10.100.33.60'

connection = pymysql.connect(
    database = 'frugal_foods',
    user = 'cvasquez',
    password = '242590909',
    host = db_link,
    cursorclass = pymysql.cursors.DictCursor
)

# # limit variable and the if statement are just a failed attempt at stopping the code from replicating data by having it check if the data already exist.
limit = []
subItems = 0
failed_attempts = 0
notFound = []
missing_items = 0
dup_items = 0

for items in divs:
#     # the next for segments are using the .find from beautifulsoup as explained before to try and filter out the items by using a attribute unique for them.
#     # .contents is used to only gather the actual text and not the code with text.
    item_name = items.find('span', {'data-testid' : "rich-text"})
    item_name = item_name.contents
    item_name = item_name[0]
    if item_name in limit:
        continue
    else:
        # try:
            limit.append(item_name)
            item_price = items.find('span', class_="fy fr fz be bf g1 dj b1")
            item_price = item_price.contents
            item_price = [item.replace('$', '') for item in item_price]
            item_price = item_price[0]
            cursor = connection.cursor()
            try:
                cursor.execute(f"SELECT `item_id` FROM `items` WHERE `item_name` = '{item_name}'")
                item_id = cursor.fetchone()
                if not item_id:
                    missing_items+=1
                    continue
                item_id = item_id['item_id']
                cursor.execute(f"SELECT `item_id` FROM `price` WHERE `item_id` = '{item_id}' AND `service_id` = '2'")
                dup = cursor.fetchone()
                if not dup:
                    pass
                else:
                    print(dup)
                    dup_items+=1
                    continue
            except:
                missing_items+=1
                continue
                # notFound.append(item_name)
            cursor.execute(f"INSERT INTO `price` (`price_value`, `item_id`, `service_id`) VALUES ('{item_price}', '{item_id}', '2')")
            connection.commit()
            cursor.close()
            # cursor.execute(f"SELECT `item_name` FROM `items`")
            # db_items = cursor.fetchall()
            # connection.commit()
            # for Values in db_items:
            #     print(Values['item_name'])
            

            # cursor = connection.cursor()
            # # this code is to make the bot automatically upload the data into the database. For now its manual input on restaurant and category but hopefully we could get the category automated.
            # cursor.execute(f'INSERT INTO `items` (`item_name`, `picture`, `restaurant_id`, `item_description`, `category_id`) VALUES ("{item_name[0]}", "{item_picture}", "1", "{item_des}", "1");')
            # connection.commit()
            # # this execute is to be able to get the id of the item uploaded to be able to assign the id on the price.
            # cursor.execute(f"SELECT `item_id` FROM `items` ORDER BY `item_id` DESC;")
            # connection.commit()
            # id = cursor.fetchone()
            # result = id['item_id']
            # # this execute uploads the price and also uses the id collected before in order to connect it with the item.
            # cursor.execute(f'INSERT INTO `price` (`price_value`, `item_id`, `service_id`) VALUES ("{item_price[0]}", "{result}","1")')
            # cursor.close()
            # connection.commit()
            subItems+=1
        # except:
        #     failed_attempts+=1
        #     pass

print()
if subItems <= 0:
    print(f'Scan failed with {subItems} submitted items and a total of {dup_items} duplicated items.')
if failed_attempts > 0:
    print(f'There was a total of {failed_attempts} failed attempts for submitted items.')
if dup_items > 0:
    print(f'There was a total of {dup_items} duplicated items that were not submitted.')
if missing_items > 0:
    print(f'There was a total of {missing_items} not found items on DB.')
if subItems > 0:
    print()
    print(f'Total of {subItems} items has been submitted to the Database. Please check if data is correct on: https://{db_link}')

driver.quit()