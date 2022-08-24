import enum
import time
from trying import Scrapping, object_type
import sqlite3
import telebot
import re


class InstructionList:
    # TODO - można zrobić jedną instruction z parametrem message i tą wartość wyciągać z np podstępnego słownika lub enumów
    # np. {
    # klucz1: tutaj_komunikat,
    # klucz2: tutaj_komunikat,
    # klucz3: tutaj_komunikat,
    # }
    # lub tworzyć klasę z enumami np:
    # class Messages(enum.Enum):
    #     klucz1 = 'tutaj_komunikat'
    #     klucz2 = 'tutaj_komunikat'
    #     klucz3 = 'tutaj_komunikat'
    # i potem uzywasz instruction_1(Messages.klucz1.value)
    def instruction_1(self):
        return """Witaj w wyszukiwarce wycieczek!
                Co chcesz zrobić?
                /1 - wyszukać aktualne oferty
                /2 - dostawać na bierząco powiadomienia"""

    def instruction_11(self):
        return """Wyszukiwanie aktualnych ofert --> ' /wyszukaj twoje filtry '
                
                Możesz użyć filtrów do przeszukiwania:
                - cena maksymalna, np. 460
                - typ okazji: wakacje / bilety / nocleg
                - słowo kluczowe, np. hiszp, all-in*, wło
                *rada: w celu zwiększenia zakresu wyszukiwania pomijaj odmieniane końcówki, 
                np. hiszp zamiast hiszpania/hiszpanii. Im krótsze słowo tym więcej dopasowań
                
                np. /wyszukaj 550 bilety all
                    /wyszukaj 600
                    /wyszukaj wakacje 2200    
                    /wyszukaj        
                """

    def instruction_21(self):
        return """Bierzące powiadomienia    
                + jeśli chcesz otrzymywać wszystkie powiadomienia zapraszamy do Holiday Chance 
                --> https://t.me/holi_chance
                + jeśli nie:
                
                Możesz użyć filtrów do otrzymywanych powiadomień:
                - cena maksymalna, np. 460
                - typ okazji: wakacje / bilety / nocleg
                - słowo kluczowe, np. hiszp, all-in*, wło
                *rada: w celu zwiększenia zakresu wyszukiwania pomijaj odmieniane końcówki, 
                np. hiszp zamiast hiszpania/hiszpanii. Im krótsze słowo tym więcej dopasowań
                
                np. /wysylaj 550 bilety all
                    /wysylaj 600
                    /wysylaj wakacje 2200    
                """


class SearchingDb:
    def __init__(self, message):
        self.price = None
        self.trip_type = None
        self.key_word = None
        self.text_message = None
        self.message = message

    def __str__(self):
        return_message = str(self.text_message)
        return return_message

    def fit_in_parameters(self):
        object_type_keys = list(object_type)
        trip_type_dict = {'wakacje': object_type_keys[0],
                          'bilety': object_type_keys[1],
                          'nocleg': object_type_keys[2]}
        words = str(self.message.text)

        price_obj = re.search('[0-9]+', words)
        if price_obj:   # TODO  self.price = price_obj.group() if price_obj else None
            self.price = price_obj.group()
            print('price', self.price)

        trip_type_obj = re.search(r'\bwakacje\b | \bbilety\b | \bnocleg\b', words)
        if trip_type_obj:
            trip_type_pl = trip_type_obj.group().strip(' ')
            self.trip_type = trip_type_dict[trip_type_pl]
            print('type obj', self.trip_type)
            # TODO - w wersji produkcyjnej (finalnej) usuń printy a jak chcesz by program logował to użyj logger
            # TODO z określeniem poziomu bledu np. logging.warning('Watch out!')

        for word in words.split():
            numbers = re.search('[0-9]+', word)
            if not numbers and word not in trip_type_dict and word != '/wyszukaj' and word != '/wysylaj':
                self.key_word = word
                print('key word', self.key_word)
                break
        return self.price, self.trip_type, self.key_word

    def db_query(self):

        db = sqlite3.connect('trips.sqlite')
        cursor = db.cursor()
        db_query = "SELECT link, context from trip WHERE "
        if self.price:
            db_query += f" price<{self.price} AND"
        if self.trip_type:
            db_query += f" type='{self.trip_type}' AND"
        if self.key_word:
            db_query += f" context LIKE '%{self.key_word}%' AND"
        db_query = db_query.strip('AND')
        cursor.execute(db_query)
        founded = cursor.fetchall()
        if founded:
            self.text_message = founded

        db.commit()


instructions = InstructionList()

bot = telebot.TeleBot("5462005082:AAFcYBB9urjaVQcDKm4rLU7aJJ_iLFcvf0U") # TODO - haslo do credentials tu zmienna tylko


@bot.message_handler(commands=['wyszukaj'])
def searching_data(message):
    searching = SearchingDb(message)
    searching.fit_in_parameters()
    searching.db_query()
    if searching.text_message:
        for search in searching.text_message:
            bot.reply_to(message, search)
    else:
        bot.reply_to(message, 'Nie ma rezultatów. Spróbuj zmienić filtry')


@bot.message_handler(commands=['1'])
def searching_info(message):
    bot.reply_to(message, instructions.instruction_11())


@bot.message_handler(commands=['2'])
def searching_info(message):
    bot.reply_to(message, {instructions.instruction_21()})


@bot.message_handler(commands=['wysylaj'])
def sending_data(message):  # TODO - do dłuższych metod dopisz docstringi, opisz też jakie wartości może przymować metoda (https://docs.python.org/3/library/typing.html) np. sending_data(message: str) -> None:
    sending = SearchingDb(message)
    filter_par = sending.fit_in_parameters()
    price, trip_type, key_word = filter_par[0], filter_par[1], filter_par[2]
    bot.reply_to(message, f'Ustawiłeś otrzymywanie powiadomień. \nTwoje filtry to:\n'
                          f'cena maksymalna: {price} \n'
                          f'rodzaj wycieczki: {trip_type} \n'
                          f'słowo kluczowe {key_word} ')

    if not price: price = 0
    if not trip_type: trip_type = ''
    if not key_word: key_word = ''
    print(price, trip_type, key_word)

    while True: # TODO : z tego można stworzyć osobną metodę np _sending_data_message_sent(price, trip_type, key_word)
        db_filtered = Scrapping()
        db_filtered.create_list()
        new_db_lines = db_filtered.db_save()

        if new_db_lines:
            for index, x in enumerate(new_db_lines):
                print(x)
                title_db, price_db,  key_word_db, trip_type_db, link_db = x[1], x[4], x[3], x[5], x[2]
                if price == 0 or int(price) > int(price_db):
                    if key_word in key_word_db and trip_type in trip_type_db:
                        bot.reply_to(message, f'Nowe oferty zgodne z twoimi flitrami! \n{title_db}\n{link_db}')
        time.sleep(300)


@bot.message_handler(func=lambda message: True)
def first_info(message):
    bot.reply_to(message, instructions.instruction_1())


bot.infinity_polling()
# TODO - utwórz klasę odpalającą i ją opisz w docstring