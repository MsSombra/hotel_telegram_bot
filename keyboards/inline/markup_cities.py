from api_req import find_city_id
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def city_markup(name_city: str) -> InlineKeyboardMarkup:
    """ Вызывает функцию для поиска городов, по найденным совпадениям создает клавиатуру с кнопками. """
    cities = find_city_id(name_city)
    destinations = InlineKeyboardMarkup()
    if cities:
        for city in cities:
            destinations.add(InlineKeyboardButton(text=city['city_name'], callback_data=city['destination_id']))
        return destinations
    else:
        return None