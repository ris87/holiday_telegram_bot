import os

from dotenv import load_dotenv

# API_KEY = os.getenv('API_KEY')
# bot = telebot.TeleBot(os.environ.get(['API_KEY'])

import sqlite3

def db_query():
    db = sqlite3.connect('trips.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT * from trip WHERE price=445")
    for x in cursor:
        print(x)
        return str(x[1:4])
    db.commit()

instruction = """Instrukcja przeszukiwania wycieczek:
                X >""" 'wycieczki tańsze niż X'


import telebot

bot = telebot.TeleBot("5462005082:AAFcYBB9urjaVQcDKm4rLU7aJJ_iLFcvf0U", parse_mode=None)
#
# @bot.message_handler(commands=['start', 'help'])
# def send_welcome(message):
#     bot.send_message(message, (db_query()))
#
# @bot.message_handler(func=lambda m: True)
# def echo_all(message):
#     bot.reply_to(message, instruction)



@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, instruction)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()

