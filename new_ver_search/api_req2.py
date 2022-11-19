import json
import requests
from config_data.config import RAPID_API_KEY
import re
from log_func import make_log
from utils.bestdeal_create_message import make_bestdeal_message
from utils.calculate_period import calculate_days


headers_api = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}


def request_to_api(mode: str, url: str, headers: dict, query: dict):
    """ Функция для обращения к API по переданным параметрам (юрл, ключ, хост и запрос). """
    make_log(lvl='info', text=f'request to api, url {url}, headers {headers}, query {query}')

    if mode == "GET":
        response = requests.get(url=url, headers=headers, params=query, timeout=10)
    elif mode == "POST":
        response = requests.post(url=url, json=query, headers=headers, timeout=10)

    try:
        if response.status_code == requests.codes.ok:
            make_log(lvl='info', text=f'response code {requests.codes.ok}')
            # print('response api', response.text)
            return response
        else:
            make_log(lvl='error', text='request to api ConnectionError')
            raise ConnectionError

    except (OSError, ConnectionError) as e:
        make_log(lvl='error', text=f'request to api {e}')


def find_city(city_name: str):
    """ Функция ищет информацию о наличии города и возвращает все совпадения. """
    make_log(lvl='info', text=f'try to find city {city_name}')

    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    query = {"q": city_name, "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}
    response = request_to_api(mode="GET", url=url, headers=headers_api, query=query)
    pattern = r'(?<="rc":"OK",).*\]'
    find = re.search(pattern, response.text)
    if find:
        cities = []
        result = json.loads(f"{{{find[0]}}}")
        print('res', result)
        for res in result['sr']:
            if res['type'] == "CITY" or res['type'] == "NEIGHBORHOOD":
                cities.append({'city_name': res["regionNames"]["shortName"], 'destination_id': res["gaiaId"]})
        print('ct', cities)
        return cities
    else:
        return None

# find_city('Лондон')


def find_address_and_photos(hotel_id: str, photos_need: bool, photos_amount: int) -> list:
    """ Делает запрос для получения адреса и при необходимости фото
    для функции send_info (Для проверки используется в make_info_message ниже). """

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
    print('fiadpho', response.text)
    pattern = r'(?<="data":{).*}{3}'
    find = re.search(pattern, response.text)
    print('f0', find[0])
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

            print('mes', messages)
            return messages

        except (KeyError, TypeError):
            return None


def make_info_message(results: dict, number_days: int, photos_need: bool, photos_amount: int) -> list:
    """ Преобразует полученный запрос в список, где каждый элемент содержит id отеля и сообщение о нем. """
    make_log(lvl='info', text=f'making messages for low or high')

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

            messages.append([hotel_id, message, photos])

        return messages
    except (KeyError, TypeError):
        return None


def find_hotels(city_id: str, hotels_amount: int, checkin_date: str, checkout_date: str, command: str,
                photos_need: bool, photos_amount: int) -> list:
    """Функция запроса по поиску отелей. Возвращает список со списками из ID отеля и строкой с сообщением"""
    make_log(lvl='info', text='find hotels worked')

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
    find = re.search(pattern, response.text)
    if find:
        results = json.loads(f"{{{find[0]}}}")
        print(results)
        number_days = calculate_days(checkin_date, checkout_date)
        new_messages = make_info_message(results, number_days, photos_need, photos_amount)
        print('nm', new_messages)
        return new_messages
    else:
        return None


# find_hotels(city_id="2114", hotels_amount=10, checkin_date='2022-10-10', checkout_date='2022-10-15',
#            command='/lowprice', photos_need=True, photos_amount=5)


def check_center_distance(hotel_info: dict, distance_max: int) -> list:
    """ Функция проверяет отели на соответствие их расстояния до центра города заданному. """
    make_log(lvl='info', text='check_center_distance worked')

    flag = False
    city_center_dist_km = 0

    dist = hotel_info['destinationInfo']['distanceFromDestination']['value']
    city_center_distance_ml = float(dist)
    city_center_distance_km = round(1.609344 * city_center_distance_ml, 1)
    if city_center_distance_km <= distance_max:
        flag = True

    return [flag, city_center_distance_km]


def make_bestdeal_message(results: dict, hotels_amount: int, distance_max: int, number_days: int,
                          photos_need: bool, photos_amount: int) -> list:
    """ Преобразует полученный запрос в список, где каждый элемент содержит id отеля и сообщение о нем. """
    make_log(lvl='info', text='make bestdeal message worked')

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

                print('mes', message)
                print('addph', to_find)

                messages.append([hotel_id, message, photos])

            if len(messages) == hotels_amount:
                break

        return messages

    except (KeyError, TypeError) as exc:
        make_log(lvl='error', text=f'bestdeal message {exc}')
        return None


def find_hotels_bestdeal(city_id: str, hotels_amount: int, checkin_date: str, checkout_date: str, photos_need: bool,
                         photos_amount: int, distance_max: int, price_min: str, price_max: str) -> list:
    """Функция запроса по поиску отелей. Возвращает список со списками из ID отеля и строкой с сообщением"""
    make_log(lvl='info', text='find hotels bestdeal worked')

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
    find = re.search(pattern, response.text)
    new_messages = []
    if find:
        results = json.loads(f"{{{find[0]}}}")
        number_days = calculate_days(checkin_date, checkout_date)
        messages = make_bestdeal_message(results, hotels_amount, distance_max, number_days, photos_need, photos_amount)
        new_messages.extend(messages)
        print('nm', new_messages)
        return new_messages

    else:
        return None


# find_hotels_bestdeal(city_id="2114", hotels_amount=10, checkin_date='2022-10-10', checkout_date='2022-10-15',
#                     photos_need=True, photos_amount=5, distance_max=15, price_min='10', price_max='100')