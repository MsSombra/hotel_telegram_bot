from datetime import datetime

from peewee import *

db = SqliteDatabase('users_history.db')


class UserReq(Model):
    """
    Класс для создания таблицы в базе данных. Записывает ID пользователя, который вводил запрос, команду,
    название города, дату и временя запроса.
    """
    user_id = CharField()
    command = CharField()
    city = CharField()
    date = DateTimeField(default=datetime.now)

    class Meta:
        database = db


class HotelsInfo(Model):
    """
    Класс для создания таблицы, хранящей текстовые сообщения о найденных отелях.
    Связана с таблицей UserReq по ID запроса.
    """
    request_id = ForeignKeyField(UserReq, related_name='request')
    text_message = CharField()

    class Meta:
        database = db


# создаем таблицы для БД, хранящей информацию об истории поиска
UserReq.create_table()
HotelsInfo.create_table()
