import json
import re

import requests

from config_data.config import RAPID_API_KEY
from log_func import make_log
from utils.bestdeal_create_message import make_bestdeal_message
from utils.calculate_period import calculate_days
from utils.create_photo_url import make_photo_url
from utils.price_create_message import make_info_message

HEADERS_API = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
    }


def request_to_api(url: str, headers: dict, querystring: dict):
    """ Универсальная функция по отправке запроса на rapidapi."""
    make_log(lvl='info', text='(func: request_to_api): worked')

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            return response.text
        else:
            return None

    except TimeoutError:
        make_log(lvl='error', text='(func: request_to_api): TimeoutError')
        return None


def find_city_id(user_town: str) -> list | None:
    """ Функция запроса с названием города. Возвращает список из словарей с названием найденных вариантов и их ID """
    make_log(lvl='info', text='find city id worked')

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    query = {"query": user_town, "locale": "ru_RU", "currency": "USD"}

    request = request_to_api(url=url,  headers=HEADERS_API, querystring=query)
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, request)

    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        cities = list()
        try:
            for city_info in suggestions['entities']:
                result_destination = re.sub(r'<.*>\S*', '', city_info['caption'])
                if result_destination.find(city_info['name']) == -1:
                    result_destination = ''.join([city_info['name'], ',', result_destination])
                cities.append({'city_name': result_destination, 'destination_id': city_info['destinationId']})
            return cities
        except KeyError:
            make_log(lvl='error', text='find city id KeyError')
            return None


def find_hotels(city_id: str, hotels_amount: str, checkin_date: str, checkout_date: str, command: str) -> list | None:
    """ Функция запроса по поиску отелей. Возвращает список со списками из ID отеля и строкой с сообщением"""
    make_log(lvl='info', text='find hotels worked')

    url = "https://hotels4.p.rapidapi.com/properties/list"
    if command == '/lowprice':
        sort_order = "PRICE"
    else:
        sort_order = "PRICE_HIGHEST_FIRST"

    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": hotels_amount, "checkIn": checkin_date,
                   "checkOut": checkout_date, "adults1": "1", "sortOrder": sort_order, "locale": "en_EN",
                   "currency": "USD"}

    response = request_to_api(url=url,  headers=HEADERS_API, querystring=querystring)

    try:
        low_price_find = re.search(r'(?<=,)"results":.+?(?=,"pagination)', response)
        if low_price_find:
            results = json.loads(f"{{{low_price_find[0]}}}")
            number_days = calculate_days(checkin_date, checkout_date)
            new_messages = make_info_message(results, number_days)
            return new_messages
        else:
            return None
    except TypeError as exc:
        make_log(lvl="error", text=f"(func: find_hotels) - {exc}")
        return None


def find_hotels_bestdeal(city_id: str, hotels_amount: int, checkin_date: str, checkout_date: str,
                         distance_max: int, price_min: str, price_max: str) -> list | None:
    """ Функция запроса по поиску отелей. Возвращает список со списками из ID отеля и строкой с сообщением """
    make_log(lvl='info', text='(func: find_hotels_bestdeal): start working')

    page_number = 1
    new_messages = []
    number_days = calculate_days(checkin_date, checkout_date)
    while True:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {"destinationId": city_id, "pageNumber": str(page_number), "pageSize": "10",
                       "checkIn": checkin_date, "checkOut": checkout_date, "adults1": "1", "priceMin": price_min,
                       "priceMax": price_max, "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": "en_EN",
                       "currency": "USD", "landmarkIds": "city center"}

        response = request_to_api(url=url, headers=HEADERS_API, querystring=querystring)
        try:
            bestdeal_find = re.search(r'(?<=,)"searchResults":.+?(?=,"sortResults)', response)
            if bestdeal_find:
                search_results = json.loads(f"{{{bestdeal_find[0]}}}")
                results = search_results['searchResults']
                messages = make_bestdeal_message(results, hotels_amount, distance_max, number_days)
                new_messages.extend(messages)
            else:
                return None

            pagination = search_results['searchResults']['pagination']
            if len(new_messages) >= hotels_amount or \
                pagination.get('currentPage') == pagination.get('nextPageNumber', page_number):
                break
            else:
                page_number += 1
        except (KeyError, TypeError) as exc:
            make_log(lvl='error', text=f'(func: find_hotels_bestdeal) - {exc}')
            return None

    make_log(lvl='info', text='(func: find_hotels_bestdeal): end working')
    return new_messages[:hotels_amount]


def find_photo_url(hotel_id: str, photo_number: int) -> list | None:
    """
    Функция запроса для получения ссылок на фотографии отеля.
    Возвращает список со ссылками на фото в количестве photo_number.
    """
    make_log(lvl='info', text='(func: find_photo_url) start working')

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
    }

    photo_response = request_to_api(url=url,  headers=headers, querystring=querystring)
    pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages)'

    try:
        find_photo = re.search(pattern, photo_response)
        if find_photo:
            results = json.loads(f"{{{find_photo[0]}}}")
            photo_url = make_photo_url(photo_number=photo_number, photo_data=results)

            make_log(lvl='info', text='(func: find_photo_url) end working')
            return photo_url
        else:
            return None
    except TypeError as exc:
        make_log(lvl='error', text=f'(func: find_photo_url) - {exc}')
        return None
