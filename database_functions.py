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


try:
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)


