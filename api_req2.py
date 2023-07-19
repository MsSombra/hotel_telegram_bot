import json
import re

import requests

from config_data.config import RAPID_API_KEY
from logging_func import logger
# from utils.bestdeal_create_message import make_bestdeal_message
from utils.calculate_period import calculate_days

HEADERS_API = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}


def request_to_api(mode: str, url: str, headers: dict, query: dict):
    """ Функция для обращения к API по переданным параметрам (юрл, ключ, хост и запрос). """
    logger.info(f'url {url}, headers {headers}, query {query}')

    if mode == "GET":
        response = requests.get(url=url, headers=headers, params=query, timeout=10)
    elif mode == "POST":
        response = requests.post(url=url, json=query, headers=headers, timeout=10)

    try:
        if response.status_code == requests.codes.ok:
            logger.info(f'response code {requests.codes.ok}')
            return response
        else:
            logger.error('ConnectionError')
            raise ConnectionError

    except (OSError, ConnectionError) as e:
        logger.error(f'{e}')


def find_city_id(city_name: str) -> list | None:
    """ Функция ищет информацию о наличии города и возвращает все совпадения. """
    logger.info(f'start working for {city_name}')

    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    query = {"q": city_name, "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}
    response = request_to_api(mode="GET", url=url, headers=HEADERS_API, query=query)

    pattern = r'(?<="rc":"OK",).*\]'
    find = re.search(pattern, response.text)
    if find:
        cities = []
        result = json.loads(f"{{{find[0]}}}")
        for res in result['sr']:
            if res['type'] == "CITY" or res['type'] == "NEIGHBORHOOD":
                cities.append({'city_name': res["regionNames"]["shortName"], 'destination_id': res["gaiaId"]})

        logger.info(f'end working for {city_name}')
        return cities
    else:
        return None


def find_address_and_photos(hotel_id: str, photos_need: bool, photos_amount: int) -> list | None:
    """
    Делает запрос для получения адреса и при необходимости фото для функций make_info_message, make_bestdeal_message.
    """
    logger.info("start working")

    url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": hotel_id
    }

    response = request_to_api(mode="POST", url=url, headers=headers, query=payload)
    pattern = r'(?<="data":{).*}{3}'

    find = re.search(pattern, response.text)
    if find:
        messages = list()
        results = json.loads(f"{{{find[0][:-2]}}}")

        try:
            hotel_address = results['propertyInfo']['summary']['location']['address']['addressLine']
            messages.append(hotel_address)

            if photos_need:
                paths = list()
                for num in range(photos_amount):
                    photo_path = results['propertyInfo']['propertyGallery']['images'][num]['image']['url']
                    paths.append(photo_path)
                messages.append(paths)
            else:
                messages.append(None)

            logger.info("end working")
            return messages

        except (KeyError, TypeError) as exc:
            logger.error(f"{exc}")
            return None


def make_info_message(results: dict, number_days: int, photos_need: bool, photos_amount: int) -> list | None:
    """ Преобразует полученный запрос в список, где каждый элемент содержит id отеля и сообщение о нем. """
    logger.info(f'low or high start')

    messages = list()
    try:
        for hotel in results['properties']:
            hotel_id = hotel['id']
            message = ''.join(['*' * 30, '\n', 'Название: ', hotel['name'], '\n'])

            city_center_distance_km = 'Не удалось определить'
            city_center_distance = hotel['destinationInfo']['distanceFromDestination']['value']
            city_center_distance_ml = float(city_center_distance)
            city_center_distance_km = str(round(1.609344 * city_center_distance_ml, 1))

            price = hotel['price']['lead']['formatted']
            total = int(price[1:])
            total_price = '$' + str(total * number_days)

            message = ''.join([message, 'Расстояние от центра (км): ', city_center_distance_km, '\n',
                               'Цена за сутки: ', price, '\n', 'Цена за период: ', total_price, '\n'])

            to_find = find_address_and_photos(hotel_id, photos_need, photos_amount)
            address = to_find[0]
            message = ''.join([message, 'Адрес: ', address, '\n'])
            photos = to_find[1]

            hotel_id = hotel['id']
            url = f'https://www.hotels.com/h{hotel_id}.Hotel-Information'
            message = ''.join([message, 'Ссылка на сайт: ', url, '\n'])

            messages.append([hotel_id, message, photos])

        logger.info(f'low or high end')
        return messages

    except (KeyError, TypeError) as exc:
        logger.error(f'{exc}')
        return None


def find_hotels(city_id: str, hotels_amount: int, checkin_date: str, checkout_date: str, command: str,
                photos_need: bool, photos_amount: int) -> list | None:
    """Функция запроса по поиску отелей. Возвращает список со списками из ID отеля и строкой с сообщением"""
    logger.info('start working')

    checkin_date_splited = checkin_date.split('-')
    checkout_date_splited = checkout_date.split('-')

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    if command == '/lowprice':
        sort_order = "PRICE_LOW_TO_HIGH"
    else:
        sort_order = "PRICE_HIGHEST_FIRST"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": city_id},
        "checkInDate": {
            "day": int(checkin_date_splited[2]),
            "month": int(checkin_date_splited[1]),
            "year": int(checkin_date_splited[0])
        },
        "checkOutDate": {
            "day": int(checkout_date_splited[2]),
            "month": int(checkout_date_splited[1]),
            "year": int(checkout_date_splited[0])
        },
        "rooms": [{"adults": 1}],
        "resultsStartingIndex": 0,
        "resultsSize": hotels_amount,
        "sort": sort_order,
        "filters": {"price": {
            "max": 10000,
            "min": 1
        }}}

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = request_to_api(mode="POST", url=url, headers=headers, query=payload)
    pattern = r'(?<=HOT.SR.sort.PROPERTY_CLASS.false"}}]}]}]},).*(?=,"propertySearchListings")'
    try:
        find = re.search(pattern, response.text)
        if find:
            results = json.loads(f"{{{find[0]}}}")
            number_days = calculate_days(checkin_date, checkout_date)
            new_messages = make_info_message(results, number_days, photos_need, photos_amount)
            logger.info('end working')
            return new_messages
        else:
            return None

    except TypeError as exc:
        logger.error(f"{exc}")
        return None


def check_center_distance(hotel_info: dict, distance_max: int) -> list:
    """ Функция проверяет отели на соответствие их расстояния до центра города заданному. """
    logger.info('worked')

    flag = False
    city_center_dist_km = 0

    dist = hotel_info['destinationInfo']['distanceFromDestination']['value']
    city_center_distance_ml = float(dist)
    city_center_distance_km = round(1.609344 * city_center_distance_ml, 1)
    if city_center_distance_km <= distance_max:
        flag = True

    return [flag, city_center_distance_km]


def make_bestdeal_message(results: dict, hotels_amount: int, distance_max: int, number_days: int,
                          photos_need: bool, photos_amount: int) -> list | None:
    """ Преобразует полученный запрос в список, где каждый элемент содержит id отеля и сообщение о нем. """
    logger.info('start working')

    messages = list()
    try:
        for i_hotel in results['properties']:
            checked_hotel = check_center_distance(i_hotel, distance_max)

            if checked_hotel[0]:
                hotel_id = i_hotel['id']
                message = ''.join(['*' * 30, '\n', 'Название: ', i_hotel['name'], '\n'])

                city_center_distance_km = 'Не удалось определить'
                city_center_distance = i_hotel['destinationInfo']['distanceFromDestination']['value']
                city_center_distance_ml = float(city_center_distance)
                city_center_distance_km = str(round(1.609344 * city_center_distance_ml, 1))

                price = i_hotel['price']['lead']['formatted']
                total = int(price[1:])
                total_price = '$' + str(total * number_days)

                message = ''.join([message, 'Расстояние от центра (км): ', city_center_distance_km, '\n',
                                   'Цена за сутки: ', price, '\n', 'Цена за период: ', total_price, '\n'])

                to_find = find_address_and_photos(hotel_id, photos_need, photos_amount)
                address = to_find[0]
                message = ''.join([message, 'Адрес: ', address, '\n'])
                photos = to_find[1]

                url = f'https://www.hotels.com/h{hotel_id}.Hotel-Information'
                message = ''.join([message, 'Ссылка на сайт: ', url, '\n'])

                messages.append([hotel_id, message, photos])

            if len(messages) == hotels_amount:
                break

        logger.info('end working')
        return messages

    except (KeyError, TypeError) as exc:
        logger.error(f'{exc}')
        return None


def find_hotels_bestdeal(city_id: str, hotels_amount: int, checkin_date: str, checkout_date: str, photos_need: bool,
                         photos_amount: int, distance_max: int, price_min: str, price_max: str) -> list | None:
    """Функция запроса по поиску отелей. Возвращает список со списками из ID отеля и строкой с сообщением"""
    logger.info('start working')

    checkin_date_splited = checkin_date.split('-')
    checkout_date_splited = checkout_date.split('-')

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    payload = {
            "currency": "USD",
            "eapid": 1,
            "locale": "ru_RU",
            "siteId": 300000001,
            "destination": {"regionId": city_id},
            "checkInDate": {
                "day": int(checkin_date_splited[2]),
                "month": int(checkin_date_splited[1]),
                "year": int(checkin_date_splited[0])
            },
            "checkOutDate": {
                "day": int(checkout_date_splited[2]),
                "month": int(checkout_date_splited[1]),
                "year": int(checkout_date_splited[0])
            },
            "rooms": [{"adults": 1}],
            "resultsStartingIndex": 0,
            "resultsSize": hotels_amount,
            "sort": "PRICE_LOW_TO_HIGH",
            "filters": {"price": {
                "max": int(price_max),
                "min": int(price_min)
            }}}

    headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }

    response = request_to_api(mode="POST", url=url, headers=headers, query=payload)
    pattern = r'(?<=HOT.SR.sort.PROPERTY_CLASS.false"}}]}]}]},).*(?=,"propertySearchListings")'
    try:
        find = re.search(pattern, response.text)
        new_messages = []
        if find:
            results = json.loads(f"{{{find[0]}}}")
            number_days = calculate_days(checkin_date, checkout_date)
            messages = make_bestdeal_message(results, hotels_amount, distance_max, number_days, photos_need, photos_amount)
            new_messages.extend(messages)
            logger.info('end working')
            return new_messages

        else:
            return None
    except TypeError as exc:
        logger.error(f"{exc}")
        return None
