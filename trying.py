from bs4 import BeautifulSoup
import requests
import sqlite3
import re

html_class = {'date': "js-calc-date",
              'title': "item__route",
              'context': "item__title",
              'price': "item__price",
              }

url_list = ["https://www.fly4free.pl/tanie-loty/loty/",
            "https://www.fly4free.pl/tanie-loty/wczasy/",
            "https://www.fly4free.pl/tanie-loty/weekend/"]

object_type = {'holiday': 'js-stats-count item item--type-3 item--with-header',
               'tickets': 'js-stats-count item item--type-1 item--with-header',
               'hotel': 'js-stats-count item item--type-2'
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
                    db_line = ['date', 'title', 'link', 'context', 'price', 'type']
                    for key in html_class:
                        sth = a.find_all(class_=html_class[key])

                        for deeper in sth:
                            html_line = deeper.text
                            if key == 'price':
                                price_fit = re.search('\d*\d*\d*\d*\d', html_line)
                                html_line = price_fit.group()
                            elif key == 'context':
                                href = re.search(r'http.*(?=\")', str(deeper))
                                db_line[2] = href.group()
                            db_line = list(map(lambda x: x.replace(key, html_line), db_line))
                    db_line[5] = promo_type
                    self.db_lines.append(db_line)


    def db_save(self):
        db = sqlite3.connect('trips.sqlite')
        # db.execute("CREATE TABLE IF NOT EXISTS trip "
        #            "(id INTEGER PRIMARY KEY, date TEXT, title TEXT, link TEXT, context TEXT, price INTEGER, type TEXT)")
        cursor = db.cursor()
        for single_line in self.db_lines:
            cursor.execute(f"SELECT * from trip WHERE link='{single_line[2]}' ")
            if not cursor.fetchall():
                query = f"INSERT INTO trip (date,title,link,context,price,type) VALUES {tuple(single_line)}"
                db.execute(query)
                self.changes_list.append(single_line)
                print('dodano', self.changes_list)
        db.commit()
        return self.changes_list

    def db_query_delete(self):
        db = sqlite3.connect('trips.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT link from trip")
        link_tuple = cursor.fetchall()
        for link_dirty in link_tuple:
            for link in link_dirty:
                page = requests.get(link)
                soup = BeautifulSoup(page.content, 'html.parser')
                soup_sold = soup.find(class_='article__soldout')
                soup_not_actual = soup.find(class_="article__offers--title")
                if soup_sold or soup_not_actual:
                    cursor.execute(f"DELETE FROM trip where link='{link}'")
                    print('DELETED: ', link)
        db.commit()
