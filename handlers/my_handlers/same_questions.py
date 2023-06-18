from datetime import date

from database.db_for_history import UserReq
from keyboards.inline.markup_cities import city_markup
from keyboards.inline.yes_no_reply import yes_or_no
from loader import bot
from log_func import make_log
from media.send_media import one_animation
from telebot.types import CallbackQuery, Message
from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar
from user_states.FSM import UserInfoState
from utils.change_language_date import change_language_date

from . import send_hotels_info


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    """
    Получает от пользователя название города. Вызывает функцию, возвращающую кнопки с найденными совпадениями.
    Записывает информацию о выбранном городе.
    """
    make_log(lvl='info', text=f'(func: get_city): city asked for chat_id {message.chat.id}')

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['request'] = UserReq.create(user_id=message.from_user.id, command=data['command'][1:], city=message.text)

    new_markup = city_markup(message.text)
    if new_markup is not None:
        bot.send_message(message.from_user.id, 'Уточните город:', reply_markup=new_markup)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text

    else:
        one_animation(message=message, file_name='wait.gif')

        bot.send_message(message.from_user.id, 'Не удалось найти такой город. Попробуйте ввести ещё раз.')
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def callback_for_cities(call: CallbackQuery) -> None:
    """
    Получает id выбранного пользователем города, записывает его.
    Создает календарь для выбора даты заезда.
    """
    make_log(lvl='info', text=f'(func: callback_for_cities): worked for chat_id {call.message.chat.id}')

    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).build()
    reply = change_language_date(text=f'Выберите дату заезда. \nВведите {LSTEP[step]}')

    bot.send_message(call.message.chat.id, reply, reply_markup=calendar)

    bot.set_state(call.message.chat.id, UserInfoState.hotels_amount)
    with bot.retrieve_data(call.message.chat.id) as data:
        data['city_id'] = call.data


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_checkin_date(call: CallbackQuery) -> None:
    """ Собирает дату заезда и записывает её. Создает второй календарь - для даты выезда. """
    make_log(lvl='info', text=f'(func: callback_for_checkin_date):  worked for chat_id {call.message.chat.id}')

    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).process(call.data)
    if not result and key:
        reply = change_language_date(f"Введите {LSTEP[step]}")
        bot.edit_message_text(reply, call.message.chat.id, call.message.message_id, reply_markup=key)

    elif result:
        bot.edit_message_text(f"Вы выбрали дату заезда: {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.message.chat.id) as data:
            data['checkin_date'] = str(result)
            data['min_checkout_date'] = result

        calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=result).build()
        reply_2 = change_language_date(text=f'Выберите дату выезда. \nВведите {LSTEP[step]}')
        bot.send_message(call.message.chat.id, reply_2, reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def callback_checkout_date(call: CallbackQuery) -> None:
    """ Собирает дату выезда и записывает её. Запрашивает количество отелей. """
    make_log(lvl='info', text=f'(func: callback_for_checkout_date): worked for chat_id {call.message.chat.id}')

    with bot.retrieve_data(call.message.chat.id) as data:
        start = data['min_checkout_date']
    result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=start).process(call.data)

    if not result and key:
        reply = change_language_date(f"Введите {LSTEP[step]}")
        bot.edit_message_text(reply, call.message.chat.id, call.message.message_id, reply_markup=key)

    elif result:
        bot.edit_message_text(f"Вы выбрали дату выезда: {result} \n",
                              call.message.chat.id,
                              call.message.message_id)
        bot.send_message(call.message.chat.id, 'Принято. Сколько отелей искать (до 10)?')
        with bot.retrieve_data(call.message.chat.id) as data:
            data['checkout_date'] = str(result)


@bot.message_handler(state=UserInfoState.hotels_amount)
def get_hotels_amount(message: Message):
    """ Получает количество отелей, записывает его. Запрашивает необходимость показа фото. """
    make_log(lvl='info', text=f'(func: get_hotels_amount): hotels amount asked for chat_id {message.chat.id}')

    if (not message.text.isdigit()) or (int(message.text) > 10):
        bot.send_message(message.from_user.id, 'Введите целое число от 1 до 10.')
    else:
        bot.send_message(message.from_user.id, 'Принято. Показывать фото отелей?', reply_markup=yes_or_no())
        bot.set_state(message.from_user.id, UserInfoState.photos_need)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels_amount'] = int(message.text)


@bot.callback_query_handler(func=lambda call: call.data.isalpha())
def get_photos_need(call: CallbackQuery) -> None:
    """
    Получает и записывает необходимость вывода фото.
    При необходимости запрашивает количество фото.
    В ином случае обобщает информацию и переходит к поиску.
    """
    make_log(lvl='info', text=f'(func: get_photos_need): asked photos need for chat_id {call.message.chat.id}')

    if call.data == 'yes':
        bot.send_message(call.message.chat.id, 'Сколько фото показывать для отеля (до 10)?')
        bot.set_state(call.message.chat.id, UserInfoState.photos_amount)
        with bot.retrieve_data(call.message.chat.id) as data:
            data['photos_need'] = True

    elif call.data == 'no':
        with bot.retrieve_data(call.message.chat.id) as data_1:
            data_1['photos_need'] = False
            data_1['photos_amount'] = 0
            command = data_1['command']

        if command == '/bestdeal':
            bot.send_message(call.message.chat.id, 'Введите максимальное расстояние от центра города(км)')
            bot.set_state(call.message.chat.id, UserInfoState.distance_max)
        else:
            one_animation(message=call.message, file_name='comparison.gif')

            text = f'Осуществляю поиск по информации:\n' \
                   f'Название города: {data_1["city"]}\n' \
                   f'Период: {data_1["checkin_date"]} - {data_1["checkout_date"]}\n' \
                   f'Количество отелей: {data_1["hotels_amount"]}'
            bot.send_message(call.message.chat.id, text)

            send_hotels_info.send_info(call.message, data_1)


@bot.message_handler(state=UserInfoState.photos_amount)
def get_photos_amount(message: Message):
    """ Получает и записывает количество фото. Обобщает информацию и переходит к поиску. """
    make_log(lvl='info', text=f'(func: get_photos_amount): asked photos amount for chat_id {message.chat.id}')

    if (not message.text.isdigit()) or (int(message.text) > 10):
        bot.send_message(message.from_user.id, 'Введите целое число от 1 до 10.')
    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photos_amount'] = int(message.text)
            command = data['command']

        if command == '/bestdeal':
            bot.send_message(message.from_user.id, 'Введите максимальное расстояние от центра города(км)')
            bot.set_state(message.from_user.id, UserInfoState.distance_max)
        else:
            one_animation(message=message, file_name='comparison.gif')

            text = f'Осуществляю поиск по информации:\n' \
                   f'Название города: {data["city"]}\n' \
                   f'Период: {data["checkin_date"]} - {data["checkout_date"]}\n' \
                   f'Количество отелей: {data["hotels_amount"]}\n' \
                   f'Количество фото: {data["photos_amount"]}'
            bot.send_message(message.from_user.id, text)
            bot.delete_state(user_id=message.from_user.id)
            send_hotels_info.send_info(message, data)
