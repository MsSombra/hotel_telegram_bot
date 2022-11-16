from loader import bot
from user_states.FSM import UserInfoState
from telebot.types import Message
from log_func import make_log


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    """ Поиск самых дешевых отелей в городе, заданном пользователем. Запрашивает город. """
    make_log(lvl='info', text=f'lowprice started for chat_id {message.chat.id}')

    bot.set_state(message.chat.id, UserInfoState.city)
    bot.send_message(message.chat.id, 'В каком городе будем искать?')
    with bot.retrieve_data(message.chat.id) as data:
        data['command'] = '/lowprice'


@bot.message_handler(commands=['highprice'])
def highprice(message: Message):
    """ Поиск самых дорогих отелей в городе, заданном пользователем. Запрашивает город. """
    make_log(lvl='info', text=f'highprice started for chat_id {message.chat.id}')

    bot.set_state(message.chat.id, UserInfoState.city)
    bot.send_message(message.chat.id, 'В каком городе будем искать?')
    with bot.retrieve_data(message.chat.id) as data:
        data['command'] = '/highprice'
