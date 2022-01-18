import sqlite3


def get_state(channel_name):
    cursor.execute(f"""select state from channels where channel_name='{channel_name}'""")
    return cursor.fetchone()[0]


def get_last_state(channel_name):
    cursor.execute(f"""select last_state from channels where channel_name='{channel_name}'""")
    return cursor.fetchone()[0]


def set_state(channel_name, value):
    cursor.execute(f"""update channels set state = {value} where channel_name='{channel_name}';""")
    sqlite_connection.commit()
    return


def set_last_state(channel_name, value):
    cursor.execute(f"""update channels set last_state = {value} where channel_name='{channel_name}';""")
    sqlite_connection.commit()
    return


def get_user_subscriptions(user_id):
    get_subscriptions_query = f"""select channel_name from subscriptions where user_id={user_id}"""
    cursor.execute(get_subscriptions_query)
    message_channels = ""
    channels_list = cursor.fetchall()
    for i in range (len(channels_list)):
        message_channels = message_channels + f"\n{str(channels_list[i][0])}"
    return message_channels


try:
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)


