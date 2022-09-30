import time
from db_processing import object_type, initialisation, get_sql_conn
import telebot
import re
from config import bot_auth_token, db_name

instruction_dict = {'1': """ Witaj w wyszukiwarce wycieczek!
                        Co chcesz zrobić?
                        /1 - wyszukać aktualne oferty
                        /2 - dostawać na bierząco powiadomienia""",

                    '2': """Wyszukiwanie aktualnych ofert --> ' /wyszukaj twoje filtry '
                
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
                        """,
                    '3': """Bierzące powiadomienia    
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
                        """}


class SearchingDb:
    """
    Searching in db dates taken from users as message
    """

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
        """
        Fit words from user's message to filter's parameters
        :return: Filter for searching in db
        """
        object_type_keys = list(object_type)
        trip_type_translate = {'wakacje': object_type_keys[0],
                               'bilety': object_type_keys[1],
                               'nocleg': object_type_keys[2]}
        words = str(self.message.text)

        price_obj = re.search('[0-9]+', words)
        self.price = price_obj.group() if price_obj else None
        print('price', self.price)

        trip_type_obj = re.search(r'\bwakacje\b | \bbilety\b | \bnocleg\b', words)
        if trip_type_obj:
            trip_type_pl = trip_type_obj.group().strip(' ')
            self.trip_type = trip_type_translate[trip_type_pl]
            print('type obj', self.trip_type)

        for word in words.split():
            numbers = re.search('[0-9]+', word)
            if not numbers and word not in trip_type_translate and word != '/wyszukaj' and word != '/wysylaj':
                self.key_word = word
                print('key word', self.key_word)
                break
        return self.price, self.trip_type, self.key_word

    def db_query(self):
        """
        Takes filters and transofrm it as query to db
        :return: db result according to filters from telegramBot user
        """
        with get_sql_conn(db_n=db_name) as cursor:
            db_query = "SELECT link, context from trip"
            if self.price or self.trip_type or self.key_word:
                db_query += " WHERE "
                if self.price:
                    db_query += f" price<{self.price} AND"
                if self.trip_type:
                    db_query += f" type='{self.trip_type}' AND"
                if self.key_word:
                    db_query += f" context LIKE '%{self.key_word}%' AND"
                db_query = db_query.rstrip('AND')

            cursor.execute(db_query)
            found = cursor.fetchall()
            if found:
                self.text_message = found


bot = telebot.TeleBot(bot_auth_token)


@bot.message_handler(commands=['wyszukaj'])
def searching_data(message):
    """
    Takes filter's parameters from TelegramBot user and according to them gives once a time db result
    """
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
    bot.reply_to(message, instruction_dict['2'])


@bot.message_handler(commands=['2'])
def searching_info(message):
    bot.reply_to(message, instruction_dict['3'])


@bot.message_handler(commands=['wysylaj'])
def sending_data(message):
    """
    Takes filter parameters from TelegramBot user and according to them gives db result every time new db data appears.
    """
    sending = SearchingDb(message)
    filter_par = sending.fit_in_parameters()
    price, trip_type, key_word = filter_par[0], filter_par[1], filter_par[2]
    bot.reply_to(message, f'Ustawiłeś otrzymywanie powiadomień. \nTwoje filtry to:\n'
                          f'cena maksymalna: {price} \n'
                          f'rodzaj wycieczki: {trip_type} \n'
                          f'słowo kluczowe: {key_word} ')

    price = price or 0
    trip_type = trip_type or ''
    key_word = key_word or ''
    print(price, trip_type, key_word)

    while True:
        new_db_lines = initialisation('db_filtered')
        if new_db_lines:
            for x in new_db_lines:
                date_db, title_db, link_db, trip_type_db, price_db, key_word_db = x[0], x[1], x[2], x[3], x[4], x[5]
                if price == 0 or int(price) > int(price_db):
                    if key_word in key_word_db and trip_type in trip_type_db:
                        bot.reply_to(message, f"Nowe oferty zgodne z twoimi filtrami!\n"
                                              f"{title_db}\n{link_db}\ncena: {price_db}")
        print('one loop')
        time.sleep(300)


@bot.message_handler(func=lambda message: True)
def first_info(message):
    """
    If telegramBot user message doesn't fit to any above, returns instruction message
    """
    bot.reply_to(message, instruction_dict['1'])


bot.infinity_polling()
