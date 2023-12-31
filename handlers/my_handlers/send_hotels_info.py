# from api_req import find_hotels, find_hotels_bestdeal, find_photo_url
from telebot.types import Message

from api_req2 import find_hotels, find_hotels_bestdeal
from database.db_for_history import HotelsInfo
from loader import bot
from logging_func import logger
from media.send_media import one_animation, one_photo, several_photos


def send_info(message: Message, dct: dict):
    """
    Отправляет сообщение с информацией по отелям. Вызывает функцию поиска информации.
    Получает список и отправляет сообщение для каждого элемента.
    """
    logger.info(f'send info started for chat_id {message.chat.id}')

    get_photo = dct['photos_need']
    number_photo = dct['photos_amount']

    if dct["command"] == '/bestdeal':
        messages_to_send = find_hotels_bestdeal(city_id=dct["city_id"],
                                                checkin_date=dct["checkin_date"],
                                                checkout_date=dct["checkout_date"],
                                                hotels_amount=dct["hotels_amount"],
                                                distance_max=dct["distance_max"],
                                                price_min=dct["price_min"],
                                                price_max=dct["price_max"],
                                                photos_need=get_photo,
                                                photos_amount=number_photo,
                                                )
    else:
        messages_to_send = find_hotels(city_id=dct["city_id"],
                                       checkin_date=dct["checkin_date"],
                                       checkout_date=dct["checkout_date"],
                                       hotels_amount=dct["hotels_amount"],
                                       command=dct["command"],
                                       photos_need=get_photo,
                                       photos_amount=number_photo,
                                       )

    if messages_to_send is not None and len(messages_to_send) > 0:
        for i_message in messages_to_send:
            bot.send_message(message.chat.id, i_message[1])
            HotelsInfo.create(request_id=dct['request'], text_message=i_message[1])

            if get_photo:
                photo_paths = i_message[2]
                several_photos(message=message, paths=photo_paths)

        one_photo(message=message, file_name='Frodo.jpg')
        bot.send_message(message.chat.id, 'Поиск окончен. ')
    else:
        one_animation(message=message, file_name='sorry.gif')
        bot.send_message(message.chat.id, 'По вашему запросу ни чего не найдено. Попробуйте еще раз')

    bot.delete_state(user_id=message.from_user.id)
