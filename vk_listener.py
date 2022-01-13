from sqlite3.dbapi2 import sqlite_version_info
import vk_api
import sqlite3
from vk_api.longpoll import VkLongPoll, VkEventType
from selenium.common.exceptions import *
from vk_token import MAIN_TOKEN
import re
import emoji


def sender(user_id, text): # отправляет сообщение id пользователю с текстом text
    vk_session.method('messages.send', {'user_id': user_id, 'message': text, 'random_id': 0})


def is_valid_channel_name(channel_name): # regex: название канала содержит только латинские буквы, цифры или подчеркивания
    new_name = re.match(r'([A-z\][\d])+', channel_name)
    if new_name is not None:
        if new_name[0] == channel_name:
            return True
        else:
            return False
    else:
        return False


def subscribe_user(channel_name, user_id): # добавляет запись о подписке пользователя user_id на канал channel_name. Если channel_name отсутствует в базе каналов, добавляет его туда
    is_active = 1
    add_channel_query = f"""insert into channels (channel_name) values ('{channel_name}');"""
    check_unique_query = f"""select count(*) from channels where channel_name='{channel_name}';"""
    check_subscribed_query = f"""select count(*) from subscriptions where channel_name='{channel_name}' and user_id={user_id};"""
    should_new_channel_be_active_query = f"""select is_active from subscriptions where user_id={user_id} limit 1;"""
    try:
        if ((cursor.execute(check_unique_query).fetchone()[0]) == 0): # если канал новый (его нет в базе каналов), он добавляется в базу
            cursor.execute(add_channel_query)

        if ((cursor.execute(check_subscribed_query).fetchone()[0]) == 0): # проверка что такой подписки нет (чтобы избежать дубликатов записей)
            try:
                if ((cursor.execute(should_new_channel_be_active_query).fetchone()[0]) == 0): # по другим подпискам пользователя определяет, должна ли подписка быть активной или неактивной при создании
                    is_active = 0
            except:
                pass
            subscribe_query = f"""insert into subscriptions (channel_name, user_id, is_active) values ('{channel_name}',{user_id}, {is_active});"""
            cursor.execute(subscribe_query)
            sender(user_id, f"Вы будете получать уведомления о стримах канала {channel_name}. \nЧтобы отписаться, введите: \nотписка {channel_name}")

        else: # если такая подписка существует
            sender(user_id, f"Вы уже подписаны на уведомления {channel_name}. \nЧтобы отписаться, введите: \nотписка {channel_name}")

        while True:
            try:
                sqlite_connection.commit()
            except:
                continue
            break

    except:
        sender(user_id, "Неверное название канала или ошибка базы данных")


def unsubscribe_user(channel_name, user_id): # удаляет запись о подписке пользователя user_id на канал channel_name. Не производит действий с базой каналов
    check_subscribed_query = f"""select count(*) from subscriptions where channel_name='{channel_name}' and user_id={user_id};"""
    unsubscribe_query = f"""delete from subscriptions where channel_name ='{channel_name}' and user_id={user_id};"""
    try:
        if ((cursor.execute(check_subscribed_query).fetchone()[0]) == 1): # если данный пользователь подписан на данный канал
            cursor.execute(unsubscribe_query)
            sqlite_connection.commit()
            sender(user_id, f"Вы отписались от уведомлений {channel_name}")
        else:
            sender(user_id, f"Отписка невозможна: вы не подписаны на уведомления {channel_name}")
    except:
        sender(user_id, "Не удалось удалить из базы данных. Попробуйте снова")


def set_active(user_id): # включает уведомления для пользователя (по умолчанию включены)
    set_active_query = f"""update subscriptions set is_active = 1 where user_id={user_id};"""
    try:
        cursor.execute(set_active_query)
        sqlite_connection.commit()
        sender(user_id, "Теперь вы получаете уведомления о стримах. \nЧтобы отменить, воспользуйтесь командой \"стоп\"")
    except:
        sender(user_id, "Не удалось установить статус \"активный\". Попробуйте еще раз")


def set_inactive(user_id): # отключает уведомления для пользователя
    set_inactive_query = f"""update subscriptions set is_active = 0 where user_id={user_id};"""
    try:
        cursor.execute(set_inactive_query)
        sqlite_connection.commit()
        sender(user_id, "Вы больше не получаете уведомления о стримах. \nЧтобы отменить, воспользуйтесь командой \"старт\"")
    except:
        sender(user_id, "Не удалось установить статус \"неактивный\". Попробуйте еще раз")


def get_commands(user_id): # отправляет сообщение с командами
    commands = emoji.emojize("""
        \U0001f4fa название_канала — подписаться на уведомление о стримах канала
        \U0001f494 отписка название_канала — отписаться от уведомлений о стримах канала
        \U0001f6d1 стоп — отключить уведомления о стримах (по умолчанию включены)
        \U0001f680 старт — включить уведомления о стримах
        \U0001f4c5 подписки — список каналов, с которых вы получаете оповещения
        \u2699 команды — список команд
                """)
    sender(user_id, commands)


def raise_input_error(user_id): # работает но хз зачем
    sender(user_id, 'Неверное название канала или неопознанная команда. Чтобы получить список команд, введите \'команды\'')


#def get_user_subscriptions(user_id): # TODO дописать


def income_message_handler(event):
    income_message_text = event.text.lower()
    user_id = event.user_id
    raw_text = income_message_text.split()
    print(raw_text)
    if len(raw_text) == 2 and raw_text[0] == 'отписка':
        if is_valid_channel_name(raw_text[1]):
            unsubscribe_user(raw_text[1], user_id)
        else:
            sender(user_id, "Отписка невозможна: неверное название канала")
    elif len(raw_text) == 1:
        if raw_text[0] == 'стоп':
            set_inactive(user_id)
        elif raw_text[0] == 'старт':
            set_active(user_id)
        elif is_valid_channel_name(raw_text[0]):
            subscribe_user(raw_text[0], user_id)
        elif raw_text[0] == 'команды':
            get_commands(user_id)
        else:
            raise_input_error(user_id)

    else:
        raise_input_error(user_id)


def input_listener(event):
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me: 
            income_message_handler(event)


vk_session = vk_api.VkApi(token = MAIN_TOKEN)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


try:
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)


for event in longpoll.listen():
    input_listener(event)
