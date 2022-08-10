import requests
from datetime import datetime
import pytz
import os
import sqlite3

from trying import Scrapping

exp = Scrapping()
exp.create_list()
exp.db_save()
instruction = exp.db_save()

telegram_auth_token = '5448084852:AAHAW__rhPpUHahuEtc1uHet-HrTVijoz3I'
telegram_group_id = 'holi_chance'
#
def send_message_on_telegram(message):
    telegram_api_url = f'https://api.telegram.org/bot{telegram_auth_token}/sendMessage?chat_id=@{telegram_group_id}&text={message}'
    tel_resp = requests.get(telegram_api_url)

def message_format():
    send_message_on_telegram("Let's see new offerts!")
    for index, x in enumerate(instruction):
        send_message_on_telegram(f"{instruction[index][1]}\n{instruction[index][2]}\n data dodania: {instruction[index][0]}")


message_format()