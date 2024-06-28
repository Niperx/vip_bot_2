import sqlite3
from datetime import datetime, timedelta
from settings import *


async def check_db():  # Проверка на ДБ, при отсутствии - создание
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    list_of_tables = cur.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='{users}';
        ''')

    print(list_of_tables.fetchall())

    if not list_of_tables.fetchall():
        print('DB Created')
        cur.execute('''
               CREATE TABLE users (
               id         INTEGER PRIMARY KEY,
               user_id    INTEGER NOT NULL
                                  UNIQUE,
               username   TEXT,
               balance    INTEGER,
               subscribe_time TEXT,
               ref_id     INTEGER,
               reg_time   TEXT
               )
           ''')
        con.commit()

    else:
        print('DB Loaded')

    con.close()


async def create_user(user_id, username=None, balance=0, ref_id=None):  # создание нового пользователя
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()
    cur.execute(f'SELECT id FROM users ORDER BY id desc')
    check = cur.fetchall()
    if check:
        cur.execute(f'SELECT id FROM users ORDER BY id desc')
        old_id = cur.fetchall()[0][0]
        new_id = old_id + 1
    else:
        new_id = 1

    user_info = (new_id, user_id, username, balance, datetime.now(), ref_id, datetime.now())
    cur.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?);", user_info)

    if ref_id is not None:
        cur.execute(f'SELECT balance FROM users WHERE user_id = {ref_id}')
        old_balance = cur.fetchall()[0][0]
        new_balance = old_balance + REF_INV_BONUS
        cur.execute(F'UPDATE users SET balance = {new_balance} WHERE user_id = {ref_id}')

    con.commit()
    con.close()


async def check_user_id(user_id):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    cur.execute(f'SELECT COUNT(*) FROM users WHERE user_id = {user_id}')
    check = cur.fetchall()[0][0]
    if check:
        return True
    else:
        return False


async def load_user(user_id):  # загрузка всей инфы о юзере
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    return result


async def get_balance(user_id):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()[0]
    return result


async def get_username(user_id):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()
    cur.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()[0]
    return result


async def add_money(user_id, money):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    # Пополнение у пользователя
    cur.execute(f'SELECT balance FROM users WHERE user_id = {user_id}')
    old_balance = cur.fetchall()[0][0]
    new_balance = old_balance + money
    cur.execute(F'UPDATE users SET balance = {new_balance} WHERE user_id = {user_id}')

    if money > 0 and REF_MODE:
        # Пополнение у реферала
        cur.execute(f'SELECT ref_id FROM users WHERE user_id = {user_id}')

        ref = cur.fetchall()[0][0]

        if ref:
            cur.execute(f'SELECT balance FROM users WHERE user_id = {ref}')
            old_balance = cur.fetchall()[0][0]
            new_balance = old_balance + int(money * (REF_PERC / 100))
            cur.execute(F'UPDATE users SET balance = {new_balance} WHERE user_id = {ref}')

    con.commit()
    con.close()


async def add_subscribe_time(user_id, time):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    # Пополнение у пользователя
    cur.execute(f'SELECT balance FROM users WHERE user_id = {user_id}')
    old_balance = cur.fetchall()[0][0]
    new_balance = old_balance + time
    cur.execute(F'UPDATE users SET balance = {new_balance} WHERE user_id = {user_id}')

    if money > 0 and REF_MODE:
        # Пополнение у реферала
        cur.execute(f'SELECT ref_id FROM users WHERE user_id = {user_id}')

        ref = cur.fetchall()[0][0]

        if ref:
            cur.execute(f'SELECT balance FROM users WHERE user_id = {ref}')
            old_balance = cur.fetchall()[0][0]
            new_balance = old_balance + int(money * (REF_PERC / 100))
            cur.execute(F'UPDATE users SET balance = {new_balance} WHERE user_id = {ref}')

    con.commit()
    con.close()


async def get_leaders(num):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    cur.execute(f'SELECT username, balance FROM users ORDER BY balance DESC LIMIT {num};')
    tops_db = cur.fetchall()

    return tops_db


async def check_payment_time(user_id):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    date_format_str = '%Y-%m-%d %H:%M:%S.%f'

    cur.execute(f'SELECT subscribe_time FROM users WHERE user_id = {user_id}')
    db_time = cur.fetchall()[0][0]
    end = datetime.strptime(db_time, date_format_str)
    now = datetime.now()
    diff = end - now

    return diff.total_seconds()


async def update_payment_time(user_id, month=1):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    print(datetime.now(), user_id)

    cur.execute(f'UPDATE users SET subscribe_time = ? WHERE user_id = ?',
                (datetime.now() + timedelta(days=month * 30), user_id))
    # тут можно изменить вид добавления времени, т.е. добавлять или изменять время
    con.commit()
    con.close()


async def change_stats(color):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    cur.execute(f'SELECT {color} FROM stats WHERE id = 1')
    number = cur.fetchall()[0][0]
    cur.execute(f'UPDATE stats SET {color} = {int(number + 1)} WHERE id = 1')

    con.commit()
    con.close()


async def get_stats():
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    cur.execute(f'SELECT red, green, black FROM stats WHERE id = 1')
    number = cur.fetchall()[0]

    return number
