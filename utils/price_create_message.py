import re
from log_func import make_log


def make_info_message(results: dict, number_days: int) -> list:
    """ Преобразует полученный запрос в список, где каждый элемент содержит id отеля и сообщение о нем. """
    make_log(lvl='info', text=f'making messages for low or high')

    messages = list()
    try:
        for hotel in results['results']:
            city_center_distance_km = 'Не удалось определить'
            message = ''.join(['*' * 30, '\n', 'Название: ', hotel['name'], '\n'])

            if 'streetAddress' in hotel['address'].keys():
                message = ''.join([message, 'Адрес: ', hotel['address']['streetAddress'], '\n'])
            else:
                message = ''.join([message, 'Адрес: ', 'Информация с адресом отсутствует', '\n'])

            for landmark in hotel['landmarks']:
                if landmark['label'].lower() == 'центр города' or landmark['label'].lower() == 'city center':
                    dist_1 = re.sub(',', '.', landmark['distance'])
                    dist_2 = re.sub(r'[^.\d]', '', dist_1)
                    city_center_distance_ml = float(dist_2)
                    city_center_distance_km = round(1.609344 * city_center_distance_ml, 1)

            price = re.sub(',', '', hotel['ratePlan']['price']['current'])
            price = re.sub(',', '', hotel['ratePlan']['price']['current'])
            one_price = int(re.sub(r'\D', '', price))
            total_price = str(one_price * number_days)
            message = ''.join([message, 'Расстояние от центра: ', str(city_center_distance_km), ' км', '\n',
                               'Цена за сутки: ', price, '\n', 'Цена за период: ', total_price, '\n'])

            hotel_id = hotel['id']
            url = f'https://hotels.com/ho{hotel_id}'
            message = ''.join([message, 'Ссылка на сайт: ', url, '\n'])

            messages.append([hotel_id, message])
        return messages
    except (KeyError, TypeError) as exc:
        make_log(lvl='error', text=f'low or high price message {exc}')
        return None
