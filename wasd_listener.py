import sqlite3
import vk_api
from vk_token import NOTIFY_TOKEN
from requests_html import *
import time
import json
from api_functions import *
from database_functions import *
import urllib 
from urllib.error import HTTPError


def get_channel_name(channel):
    return channel[0]


def is_online(channel):
    try:
        channel_status = channel.html.xpath('//*[@id="channelInfo"]/div/wasd-user-plays/div/span')
        if channel_status[0].text == 'стримит':
            return True
        else:
            return False
    except IndexError:
        pass


def get_title(channel):
    title = channel.html.xpath('//*[@id="streamInfo"]/wasd-player-info/div/div/div/div[2]/div[1]/div[1]/div/div/span')
    return title[0].text


def get_category(channel):
    category = channel.html.xpath('//*[@id="channelInfo"]/div/wasd-user-plays/div/a[2]')
    return category[0].text


def second_sender(id, text):
    second_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0})


def notify_online(channel_name, title, category):
    get_subscriptions_query = f"""select user_id from subscriptions where channel_name='{channel_name}'"""
    cursor.execute(get_subscriptions_query)
    user_list = cursor.fetchall()
    print(channel_name)
    print(title)
    print(category)
    message_text = f"{channel_name} начал стрим: {title} ({category}) https://wasd.tv/{channel_name}"
    for user in user_list:
        second_sender(user, message_text)


def one_channel_listener(channel, hsession):
        start_time = time.time()
        channel_name = get_channel_name(channel)
        print(f"Текущий канал: {channel_name}")
        channel_view = hsession.get(f'https://wasd.tv/{channel_name}', cookies=None)
        channel_view.html.render(sleep=1, timeout=5)
        if is_online(channel_view):
            set_state(channel, 1)
            if get_state(channel) > get_last_state(channel):
                set_last_state(channel, 1)
                notify_online(channel_name,get_title(channel_view),get_category(channel_view))
                print(f"{channel_name} запустил стрим, отправлены уведомления")
            else:
                print(f"{channel_name} уже ведет трансляцию, уведомления не отправлены")
        else:
            set_last_state(channel, get_state(channel))
            set_state(channel, 0)
            print(f"Канал {channel_name} не в сети, действий не произведено")
        channel_view.close()
        print("Соединение закрыто")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Затраченное время: {elapsed_time} секунд")


def api_channel_listener(channel):
        channel_name = get_channel_name(channel)
        start_time = time.time()
        print(f"Текущий канал: {channel_name}")
        try:
            with urllib.request.urlopen(f"https://wasd.tv/api/v2/broadcasts/public?channel_name={channel_name}") as url:
                channel_data = json.loads(url.read().decode())
        except HTTPError:
             return   
        if api_is_online(channel_data):
            set_state(channel_name, 1)
            if get_state(channel_name) > get_last_state(channel_name):
                set_last_state(channel_name, 1)
                notify_online(channel_name,api_title(channel_data),api_category(channel_data))
                print(f"{channel_name} запустил стрим, отправлены уведомления")
            else:
                print(f"{channel_name} уже ведет трансляцию, уведомления не отправлены")
        else:
            set_last_state(channel_name, get_state(channel_name))
            set_state(channel_name, 0)
            print(f"Канал {channel_name} не в сети, действий не произведено")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Затраченное время: {elapsed_time} секунд")
        time.sleep(1)


def main():
    while True:
        get_channels_query = """select channel_name from channels"""
        cursor.execute(get_channels_query)
        channels_list = cursor.fetchall()
        for channel in channels_list:
            api_channel_listener(channel)
            #one_channel_listener(channel, hsession)
        time.sleep(1)


try:
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)


second_session = vk_api.VkApi(token = NOTIFY_TOKEN)
session_api = second_session.get_api()
hsession = HTMLSession()
        

if __name__ == "__main__":
    main()