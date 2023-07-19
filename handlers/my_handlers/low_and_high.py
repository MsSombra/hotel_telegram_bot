from telebot.types import Message

from loader import bot
from logging_func import logger
from user_states.FSM import UserInfoState


@bot.message_handler(commands=['lowprice'])
def low_price(message: Message) -> None:
    """ Поиск самых дешевых отелей в городе, заданном пользователем. Запрашивает город. """
    logger.info(f'low price started for chat_id {message.chat.id}')

    bot.set_state(message.chat.id, UserInfoState.city)
    bot.send_message(message.chat.id, 'В каком городе будем искать?')
    with bot.retrieve_data(message.chat.id) as data:
        data['command'] = '/lowprice'


@bot.message_handler(commands=['highprice'])
def high_price(message: Message):
    """ Поиск самых дорогих отелей в городе, заданном пользователем. Запрашивает город. """
    logger.info(f'high price started for chat_id {message.chat.id}')

    bot.set_state(message.chat.id, UserInfoState.city)
    bot.send_message(message.chat.id, 'В каком городе будем искать?')
    with bot.retrieve_data(message.chat.id) as data:
        data['command'] = '/highprice'
