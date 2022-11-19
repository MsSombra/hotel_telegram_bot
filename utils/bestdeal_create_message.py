import re
from log_func import make_log


def check_center_distance(hotel_info: dict, distance_max: int) -> list:
    """ Функция проверяет отели на соответствие их расстояния до центра города заданному. """
    make_log(lvl='info', text='check_center_distance worked')
    flag = False
    city_center_dist_km = 0
    for i_hotel in hotel_info['landmarks']:
        if i_hotel['label'].lower() == 'центр города' or i_hotel['label'].lower() == 'city center':
            dist_1 = re.sub(',', '.', i_hotel['distance'])
            dist_2 = re.sub(r'[^.\d]', '', dist_1)
            city_center_distance_ml = float(dist_2)
            city_center_distance_km = round(1.609344 * city_center_distance_ml, 1)
            if city_center_distance_km <= distance_max:
                flag = True
    return [flag, city_center_distance_km]


def make_bestdeal_message(results: dict, hotels_amount: int, distance_max: int, number_days: int) -> list:
    """ Преобразует полученный запрос в список, где каждый элемент содержит id отеля и сообщение о нем. """
    make_log(lvl='info', text='make_bestdeal_message worked')

    messages = list()
    try:
        for i_hotel in results['results']:
            checked_hotel = check_center_distance(i_hotel, distance_max)

            if checked_hotel[0]:
                message = ''.join(['*' * 30, '\n', 'Название: ', i_hotel['name'], '\n'])

                if 'streetAddress' in i_hotel['address'].keys():
                    message = ''.join([message, 'Адрес: ', i_hotel['address']['streetAddress'], '\n'])
                else:
                    message = ''.join([message, 'Адрес: ', 'Информация с адресом отсутствует', '\n'])

                price = re.sub(',', '', i_hotel['ratePlan']['price']['current'])
                one_price = int(re.sub(r'\D', '', price))
                total_price = str(one_price * number_days)
                message = ''.join([message, 'Расстояние от центра: ',  str(checked_hotel[1]), ' км', '\n',
                                   'Цена за сутки: ', price, '\n', 'Цена за период: ', total_price, '\n'])

                hotel_id = i_hotel['id']
                url = f'https://hotels.com/ho{hotel_id}'
                message = ''.join([message, 'Ссылка на сайт: ', url, '\n'])
                messages.append([hotel_id, message])

            if len(messages) == hotels_amount:
                break

        return messages

    except (KeyError, TypeError) as exc:
        make_log(lvl='error', text=f'bestdeal message {exc}')
        return None
