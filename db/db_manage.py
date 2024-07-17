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


async def change_stats(num):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    current_id = datetime.now().month
    cur.execute(f'SELECT {num} FROM stats WHERE id = {current_id}')
    number = cur.fetchall()[0][0]
    cur.execute(f'UPDATE stats SET {num} = {int(number + 1)} WHERE id = {current_id}')

    con.commit()
    con.close()


async def get_stats_all():
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    cur.execute(f'SELECT one, three, one_prem, three_prem FROM stats')
    stats = cur.fetchall()
    one, three, one_prem, three_prem = 0, 0, 0, 0
    for i in stats:
        one += i[0]
        three += i[1]
        one_prem += i[2]
        three_prem += i[3]

    return one, three, one_prem, three_prem


async def get_stats_of_month():
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    now = datetime.now()
    print(now.month)

    cur.execute(f'SELECT one, three, one_prem, three_prem FROM stats WHERE id = {now.month}')
    number = cur.fetchall()[0]

    return number


async def count_users():
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    cur.execute(f'SELECT COUNT(*) FROM users')
    count_users = cur.fetchall()[0][0]

    return count_users


async def count_users_buyers():
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    cur.execute(f'SELECT * FROM users')
    count_users = cur.fetchall()

    date_format_str = '%Y-%m-%d %H:%M:%S.%f'

    cnt = 0
    for user in count_users:
        end_time = datetime.strptime(user[4], date_format_str)
        if end_time > datetime.now():
            cnt += 1

    return cnt


async def get_users_list():
    conn = sqlite3.connect('db/main.db')
    cur = conn.cursor()

    cur.execute('SELECT user_id FROM users')
    users = cur.fetchall()

    return users
