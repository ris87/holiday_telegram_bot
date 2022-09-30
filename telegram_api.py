import requests
import time
from db_processing import initialisation, db_query_delete
from config import telegram_auth_token, telegram_group_id


def send_message_on_telegram(message):
    telegram_api_url = f'https://api.telegram.org/bot{telegram_auth_token}/sendMessage?chat_id=@{telegram_group_id}&text={message}'
    tel_resp = requests.get(telegram_api_url)


def message_format(new_db_lines):
    """
    Takes new data from db if append and send on TelegramBot in fitted format
    :param new_db_lines: list with new db data
    :return: message send by TelegramBot with new_db_lines data
    """
    if new_db_lines:
        send_message_on_telegram("Zobacz nowe oferty!")
        for x in new_db_lines:
            date_db, title_db, link_db, trip_type_db, price_db,  key_word_db = x[0], x[1], x[2], x[3], x[4], x[5]
            send_message_on_telegram(f"{title_db}\n{link_db}\ncena: {price_db}")


while True:
    # db_query_delete()
    message_format(initialisation('exp'))
    print('one loop end')
    time.sleep(3600)
