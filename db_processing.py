from bs4 import BeautifulSoup
import requests
import sqlite3
import re
from config import db_name
import contextlib

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


@contextlib.contextmanager
def get_sql_conn(db_n):
    """Context manager to automatically create DB cursor and later close DB connection"""
    db = sqlite3.connect(db_n)
    cursor = db.cursor()
    try:
        yield cursor
    finally:
        db.commit()
        db.close()


class Scrapping:
    """
    Class for scrapping websites from url_list to find data: date, title, link, context, price, type and save it to db
    """

    def __init__(self):
        self.db_lines = []
        self.changes_list = []

    def create_list(self):
        """
        Takes url from url_list and scrapped data fit into tuple
        :return: list of tuples. Single tuple is data for single trip and takes single line in db
        """
        for url in url_list:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            for promo_type in object_type:
                html_offer_list = soup.find_all(class_=object_type[promo_type])

                for html_offer in html_offer_list[0:2]:
                    db_line = ['date', 'title', 'link', 'context', 'price', 'type']
                    for key in html_class:
                        span = html_offer.find_all(class_=html_class[key])
                        db_line_item = span[0].text
                        if key == 'price':
                            price_fit = re.search('\d*\d*\d*\d*\d', db_line_item)
                            db_line_item = price_fit.group()
                        elif key == 'context':
                            href = re.search(r'http.*(?=\")', str(span[0]))
                            db_line[2] = href.group()
                        db_line = list(map(lambda x: x.replace(key, db_line_item), db_line))
                    db_line[5] = promo_type
                self.db_lines.append(db_line)

    def db_save(self):
        """
        Save tuple with scrapped data to db if link already not exist in db
        :return: list of tuples which was added to db
        """
        with get_sql_conn(db_n=db_name) as cursor:

            for single_line in self.db_lines:
                cursor.execute(f"SELECT * from trip WHERE link='{single_line[2]}' ")
                if not cursor.fetchall():
                    query = f"INSERT INTO trip (date,title,link,context,price,type) VALUES {tuple(single_line)}"
                    cursor.execute(query)
                    self.changes_list.append(single_line)
                    print('dodano', single_line)
            return self.changes_list


def db_query_delete():
    """
    Checking every link in db and delete it if is already soldout or not actual
    """
    with get_sql_conn(db_n=db_name) as cursor:

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


def initialisation(instance_name: str) -> list:
    """
    Make new instance, scrap url and save this data to db
    :param instance_name: Name for new instance
    :return: List of lines added to db
    """
    instance_name = Scrapping()
    instance_name.create_list()
    new_db_lines = instance_name.db_save()
    return new_db_lines

