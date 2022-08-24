from bs4 import BeautifulSoup
import requests
import sqlite3
import re
#TODO Usuniecie nieuzywanych bibliotek (low)
# TODO - dodanie requirments z używanymi bibliotekami i ich wymaganymi wersjami (low)

db = sqlite3.connect('trips.sqlite')    # TODO ubranie w klasę z metodą (medium)
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
            #def delete where link=link     # TODO - usuniecie nieuzywanego kodu (low), powoduje mniej zamiesznaia w przyszlosci bo nie wiesz czy to jest potrzebne czy nie , czy tymczasowo zahaszowane, ewentualnie z dopiskiem jak potrzebne i po co
        # soup_not_actual = soup.find_all(class_="article__offers--title")
        # if soup_not_actual:
        #     print(link)

# TODO - opisz readme
# TODO - JAK NA PIERWSZY KOD TO BARDZO DOBRZE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO - ILOŚĆ UWAG NIE ŚWIADCZY O TYM ŻE KOD JEST ZŁY A TYLKO  O TYM CO MOŻNA POPRAWIĆ BY BYŁ LEPSZY, O ELEMENTY KTÓRE NP. MOGŁAŚ NIE ZNAĆ (NP. LOGGING, ENUMS)

# TODO - PO WPROWADZENIU WSZYSTKICH ZMIAN KOLEJNYM ZADANIEM BEDZIE ZAMKNIECIE TEGO W DOCKERZE I ODPALENIE NA SERWERZE BY DZIAŁĄŁO CIĄGLE