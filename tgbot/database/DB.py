import sqlite3
import time
from dataclasses import dataclass

from aiogram.types import Message


@dataclass
class User:
    telegram_id: int
    username: str
    fullname: str
    registration_time: int
    balance: int


@dataclass
class BlockUser:
    telegram_id: int
    username: str
    fullname: str
    registration_time: int
    balance: int


@dataclass
class MessageSend:
    Role: str
    Message: str
    Media_content: str


@dataclass
class MessageAutoSend:
    Role: str
    Message: str
    Media_content: str
    Schedule: bool
    Time_schedule: int
    Keyboard: str


@dataclass
class Products:
    Title: str
    Description: str
    Price: int
    Payment_link: str


class Database:
    def __init__(self):
        self.conn_us = sqlite3.connect('Users.db')
        self.cur_us = self.conn_us.cursor()
        self.cur_us.execute("""CREATE TABLE IF NOT EXISTS Пользователи(
        Telegram_id INT PRIMARY KEY,
        Username TEXT,
        Fullname TEXT,
        Registration_time TEXT,
        Balance INT
        );""")
        self.conn_us.commit()
        self.conn_set = sqlite3.connect('Settings.db')
        self.cur_set = self.conn_set.cursor()
        self.cur_set.execute("""CREATE TABLE IF NOT EXISTS Сообщения(
        Role TEXT,
        Message TEXT,
        Media_content TEXT
        );""")
        self.conn_set.commit()
        self.cur_set.execute("""CREATE TABLE IF NOT EXISTS АвтоСообщения(
        Role TEXT,
        Message TEXT,
        Media_content TEXT,
        Schedule BOOL,
        Time_schedule INT,
        Keyboard TEXT)
        ;""")
        self.conn_set.commit()
        self.cur_set.execute("""CREATE TABLE IF NOT EXISTS Товары(
        Title TEXT,
        Description TEXT,
        Price INT,
        Payment_link TEXT
        );""")
        self.conn_set.commit()
        self.cur_set.execute("""CREATE TABLE IF NOT EXISTS Заблокированные(
        Telegram_id INT PRIMARY KEY,
        Username TEXT,
        Fullname TEXT,
        Registration_time TEXT
        );""")
        self.conn_set.commit()
        self.cur_set.execute("""CREATE TABLE IF NOT EXISTS Основные(
        Token TEXT,
        Admins TEXT
        );""")
        self.conn_set.commit()

    '''ПОЛЬЗОВАТЕЛИ'''

    def add_user(self, message: Message):
        telegram_id = message.from_user.id
        username = message.from_user.username
        fullname = message.from_user.first_name + '' + message.from_user.last_name
        registration_time = int(time.time())
        balance = 1
        self.cur_us.execute("INSERT INTO Пользователи VALUES(?,?,?,?,?);",
                            [telegram_id, username, fullname, registration_time, balance])
        self.conn_us.commit()

    def update(self, index, val, user):
        self.cur_us.execute(f"UPDATE Пользователи SET {index} = '{val}' WHERE Telegram_id = {user};")
        self.conn_us.commit()

    def user_exist(self, user_id):
        self.cur_us.execute(f"SELECT COUNT(*) FROM Пользователи WHERE Telegram_id = {user_id}")
        count = self.cur_us.fetchone()[0]
        if count != 0:
            return True
        else:
            return False

    def get_user(self, user_id):
        self.cur_us.execute("SELECT * FROM Пользователи")
        users = self.cur_us.fetchall()
        if len(users) != 0:
            for i in range(len(users)):
                if users[i][0] == user_id:
                    return User(telegram_id=users[i][0], username=users[i][1], fullname=users[i][2],
                                registration_time=users[i][3], balance=users[i][4])

    def up_sub(self):
        self.cur_us.execute("SELECT * FROM Пользователи")
        users = self.cur_us.fetchall()
        if len(users) != 0:
            return users

    '''Заблокированные'''

    def add_block_user(self, telegram_id):
        user = self.get_user(telegram_id)
        user = [user.telegram_id, user.username, user.fullname, user.registration_time, user.balance]
        self.cur_set.execute("INSERT INTO Заблокированные VALUES(?,?,?,?,?);", user)
        self.conn_set.commit()

    def get_block_user(self, telegram_id):
        self.cur_set.execute("SELECT * FROM Заблокированные WHERE Telegram_id =?", [telegram_id])
        users = self.cur_set.fetchall()
        if len(users) == 0:
            for i in range(len(users)):
                if users[i][0] == telegram_id:
                    return BlockUser(telegram_id=users[i][0], username=users[i][1], fullname=users[i][2],
                                     registration_time=users[i][3], balance=users[i][4])

    def del_block_user(self, telegram_id):
        self.cur_set.execute("DELETE FROM Заблокированные WHERE Telegram_id =?", [telegram_id])
        self.conn_set.commit()

    '''Сообщения'''

    def get_message(self, role):
        self.cur_set.execute("SELECT * FROM Сообщения")
        message = self.cur_set.fetchall()
        if len(message) != 0:
            for i in range(len(message)):
                if message[i][0] == role:
                    return MessageSend(Role=message[i][0], Message=message[i][1], Media_content=message[i][2])

    def update_message(self, role: str, message: str):
        self.cur_us.execute(f"UPDATE Сообщения SET Message = '{message}' WHERE Role = {role};")
        self.conn_us.commit()

    def get_auto_message(self, role: str):
        self.cur_set.execute("SELECT * FROM АвтоСообщения")
        message = self.cur_set.fetchall()
        if len(message) != 0:
            for i in range(len(message)):
                if message[i][1] == role:
                    return MessageAutoSend(
                        Role=message[i][0],
                        Message=message[i][1],
                        Media_content=message[i][3],
                        Schedule=message[i][4],
                        Time_schedule=message[i][5],
                        Keyboard=message[i][6])

    def update_auto_message(self, role: str, message: str, media_content: str = None, keyboard: str = None,
                            schedule: bool = False, time_schedule: int = None):
        if media_content is not None:
            self.cur_set.execute(f"UPDATE АвтоСообщения SET Media_content = '{media_content}' WHERE Role = {role};")
        if schedule:
            self.cur_set.execute(f"UPDATE АвтоСообщения SET Schedule = '{schedule}' WHERE Role = {role};")
        if time_schedule is not None:
            self.cur_set.execute(f"UPDATE АвтоСообщения SET Time_schedule = '{time_schedule}' WHERE Role = {role};")
        if keyboard is not None:
            self.cur_set.execute(f"UPDATE АвтоСообщения SET Keyboard = '{keyboard}' WHERE Role = {role};")
        self.cur_set.execute(f"UPDATE АвтоСообщения SET Message = '{message}' WHERE Role = {role};")
        self.conn_set.commit()

    def add_auto_message(self, role: str, message: str, media_content: str = None, schedule: bool = False,
                         time_schedule: int = None, keyboard: str = None):
        self.cur_set.execute("INSERT INTO АвтоСообщения VALUES(?,?,?,?,?,?);",
                             [role, message, media_content, schedule, time_schedule, keyboard])
        self.conn_set.commit()

    def delete_auto_message(self, role):
        self.cur_us.execute(f"DELETE FROM АвтоСообщения WHERE Role = '{role}';")
        self.conn_us.commit()

    '''Товары'''

    def get_product(self, title):
        self.cur_set.execute("SELECT * FROM Товары")
        product = self.cur_set.fetchall()
        if len(product) != 0:
            for i in range(len(product)):
                if product[i][0] == title:
                    return Products(Title=product[i][0], Description=product[i][1], Price=product[i][2],
                                    Payment_link=product[i][3])

    def add_product(self, title: str, description: str, price: int, payment_link: str):
        self.cur_set.execute("INSERT INTO Товары VALUES(?,?,?,?);",
                             [title, description, price, payment_link])
        self.conn_set.commit()

    def update_product(self, title: str, description: str = None, price: int = None, payment_link: str = None):
        if description is not None:
            self.cur_set.execute(f"UPDATE Товары SET Description = '{description}' WHERE Title = {title};")
        if price is not None:
            self.cur_set.execute(f"UPDATE Товары SET Price = '{price}' WHERE Title = {title};")
        if payment_link is not None:
            self.cur_set.execute(f"UPDATE Товары SET Payment_link = '{payment_link}' WHERE Title = {title};")
        self.cur_set.execute(f"UPDATE Товары SET Title = '{title}' WHERE Title = {title};")

    def delete_product(self, title):
        self.cur_set.execute(f"DELETE FROM Товары WHERE Title = '{title}';")
        self.conn_set.commit()

    def up_product(self):
        self.cur_set.execute("SELECT * FROM Товары")
        products = self.cur_set.fetchall()
        if len(products) != 0:
            return products

    '''Основные'''

    def update_token(self, token):
        self.cur_set.execute(f"UPDATE Основные SET Token = '{token}';")

    def get_token(self):
        self.cur_set.execute("SELECT * FROM Основные WHERE Token IS NOT NULL;")
        token = self.cur_set.fetchone()
        return token

    def get_admins(self):
        self.cur_set.execute("SELECT * FROM Основные WHERE Admins IS NOT NULL;")
        admins = self.cur_set.fetchone()
        return admins

    def update_admins(self, admins):
        self.cur_set.execute(f"UPDATE Основные SET Admins = '{admins}' WHERE Admins IS NOT NULL;")
        self.conn_set.commit()

