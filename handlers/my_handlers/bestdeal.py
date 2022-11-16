from log_func import make_log
from loader import bot
from telebot.types import Message
from user_states.FSM import UserInfoState
from . import send_hotels_info
from media.send_media import one_animation


@bot.message_handler(commands=['bestdeal'])
def bestdeal_reply(message: Message) -> None:
    """ Поиск отелей по цене и расстоянию до центра в городе, заданном пользователем. Запрашивает город. """
    make_log(lvl='info', text=f'bestdeal started for chat_id {message.chat.id}')
    bot.set_state(message.chat.id, UserInfoState.city)
    bot.send_message(message.chat.id, 'В каком городе будем искать?')
    with bot.retrieve_data(message.chat.id) as data:
        data['command'] = '/bestdeal'


@bot.message_handler(state=UserInfoState.distance_max)
def get_distance_max(message: Message) -> None:
    """ Принимает и записывает максимальное расстояние до центра города. Запрашивает минимальную цену. """
    make_log(lvl='info', text=f'max distance asked for chat_id {message.chat.id}')

    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите минимальную стоимость в $')
        bot.set_state(message.from_user.id, UserInfoState.price_min)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['distance_max'] = int(message.text)

    else:
        bot.send_message(message.from_user.id, 'Сообщение должно содержать только цифры')


@bot.message_handler(state=UserInfoState.price_min)
def get_price_min(message: Message) -> None:
    """ Принимает и записывает минимальную цену. Запрашивает максимальную цену. """
    make_log(lvl='info', text=f'min price asked for chat_id {message.chat.id}')

    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите максимальную стоимость в $')
        bot.set_state(message.from_user.id, UserInfoState.price_max)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_min'] = message.text

    else:
        bot.send_message(message.from_user.id, 'Сообщение должно содержать только цифры')


@bot.message_handler(state=UserInfoState.price_max)
def get_price_max(message: Message) -> None:
    """ Принимает и записывает максимальную цену. Переходит к поиску. """
    make_log(lvl='info', text=f'max price asked for chat_id {message.chat.id}')
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_max'] = message.text

        one_animation(message=message, file_name='comparison2.gif')

        text = f'Осуществляю поиск по информации:\nНазвание города: {data["city"]}\n' \
               f'Период: {data["checkin_date"]} - {data["checkout_date"]}\n' \
               f'Количество отелей: {data["hotels_amount"]}\nКоличество фото: {data["photos_amount"]}\n' \
               f'Расстояние до центра (км): {data["distance_max"]}\n' \
               f'Диапазон цен ($): {data["price_min"]} - {data["price_max"]}'
        bot.send_message(message.from_user.id, text)
        bot.delete_state(user_id=message.from_user.id)
        send_hotels_info.send_info(message, data)

    else:
        bot.send_message(message.from_user.id, 'Сообщение должно содержать только цифры')
