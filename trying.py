from bs4 import BeautifulSoup
import requests
import sqlite3
import re

html_class = {'date': "js-calc-date",
            'title': "item__route",
            'context':"item__title",
            'price':"item__price",
              }

url_list = ["https://www.fly4free.pl/tanie-loty/loty/", "https://www.fly4free.pl/tanie-loty/wczasy/", "https://www.fly4free.pl/tanie-loty/weekend/"]

object_type = {'holiday':'js-stats-count item item--type-3 item--with-header',
               'tickets': 'js-stats-count item item--type-1 item--with-header',
               'hotel':'js-stats-count item item--type-2'
               }


class Scrapping:

    def __init__(self):
        self.db_lines = []
        self.changes_list = []

    def create_list(self):
        for url in url_list:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            for promo_type in object_type:
                single_soup = soup.find_all(class_=object_type[promo_type])

                for a in single_soup[0:2]:
                    db_line = []
                    for key in html_class:
                        sth = a.find_all(class_=html_class[key])

                        for deeper in sth:
                            if key == 'price':
                                dirty_price = deeper.text
                                price_fit=re.search('\d*\d*\d*\d*\d', dirty_price)
                                clean_price=price_fit.group()
                                db_line.append(clean_price)
                            elif key == 'context':
                                href = re.search(r'http.*(?=\")', str(deeper))
                                clean_href = href.group()
                                db_line.append(clean_href)
                                db_line.append(deeper.text)
                            else:
                                db_line.append(deeper.text)
                    db_line.append(promo_type)
                    self.db_lines.append(db_line)

    def db_save (self):
        db = sqlite3.connect('trips.sqlite')
        db.execute("CREATE TABLE IF NOT EXISTS trip (id INTEGER PRIMARY KEY, date TEXT, title TEXT, link TEXT, context TEXT, price INTEGER, type TEXT)")
        cursor = db.cursor()
        for single_line in self.db_lines:

            cursor.execute(f"SELECT * from trip WHERE link='{single_line[2]}' ")
            if not cursor.fetchall():
                print('not in db. Adding: ', single_line)
                query = f"INSERT INTO trip (date,title,link,context,price,type) VALUES {tuple(single_line)}"
                db.execute(query)
                self.changes_list.append(single_line)
        db.commit()
        return self.changes_list



