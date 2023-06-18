# from api_req import find_city_id
from api_req2 import find_city_id
from log_func import make_log
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def city_markup(name_city: str) -> InlineKeyboardMarkup | None:
    """ Вызывает функцию для поиска городов, по найденным совпадениям создает клавиатуру с кнопками. """

    cities = find_city_id(name_city)
    destinations = InlineKeyboardMarkup()
    if cities:
        for city in cities:
            destinations.add(InlineKeyboardButton(text=city['city_name'], callback_data=city['destination_id']))

        make_log(lvl="info", text="(func: city_markup): city markup made")
        return destinations
    else:
        make_log(lvl="info", text="(func: city_markup): no cities")
        return None
