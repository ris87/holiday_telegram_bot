import requests
import time
from trying import Scrapping

telegram_auth_token = '5448084852:AAHAW__rhPpUHahuEtc1uHet-HrTVijoz3I'
telegram_group_id = 'holi_chance'


def send_message_on_telegram(message):
    telegram_api_url = f'https://api.telegram.org/bot{telegram_auth_token}/sendMessage?chat_id=@{telegram_group_id}&text={message}'
    tel_resp = requests.get(telegram_api_url)


def message_format():
    if instruction:
        send_message_on_telegram("Zobacz nowe oferty!")
        for index, x in enumerate(instruction):
            date, title, link, price = instruction[index][0], instruction[index][1], instruction[index][2], instruction[index][4]
            send_message_on_telegram(f"{title}\n{link}\ndata dodania: {date}\n cena: {price}")


while True:
    exp = Scrapping()
    exp.db_query_delete()
    exp.create_list()
    instruction = exp.db_save()
    message_format()
    print('one loop end')
    time.sleep(30)
