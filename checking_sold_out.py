from bs4 import BeautifulSoup
import requests
import sqlite3
import re


db = sqlite3.connect('trips.sqlite')
cursor = db.cursor()
db_query = "SELECT link from trip"
cursor.execute(db_query)
link_tuple = cursor.fetchall()

for link_dirty in link_tuple:
    for link in link_dirty:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        soup_sold = soup.find(class_='article__soldout')
        if soup_sold:
            print(link)
            #def delete where link=link
        # soup_not_actual = soup.find_all(class_="article__offers--title")
        # if soup_not_actual:
        #     print(link)

