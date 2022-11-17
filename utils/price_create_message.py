import re
from log_func import make_log


def make_info_message(results: dict) -> list:
    """ Преобразует полученный запрос в список, где каждый элемент содержит id отеля и сообщение о нем. """
    make_log(lvl='info', text=f'making messages for low or high')

    messages = list()
    try:
        for hotel in results['results']:
            city_center_distance = 'Не удалось определить'
            message = ''.join(['*' * 30, '\n', 'Название: ', hotel['name'], '\n'])

            if 'streetAddress' in hotel['address'].keys():
                message = ''.join([message, 'Адрес: ', hotel['address']['streetAddress'], '\n'])
            else:
                message = ''.join([message, 'Адрес: ', 'Информация с адресом отсутствует', '\n'])

            for landmark in hotel['landmarks']:
                if landmark['label'].lower() == 'центр города' or landmark['label'].lower() == 'city center':
                    city_center_distance = landmark['distance']
            price = re.sub(',', '', hotel['ratePlan']['price']['current'])
            total = re.sub(',', '', hotel['ratePlan']['price']['fullyBundledPricePerStay'])
            total_price = re.search(r'\$\d+', total)
            message = ''.join([message, 'Расстояние от центра: ', city_center_distance, '\n',
                               'Цена за сутки: ', price, '\n', 'Цена за период: ', total_price.group(), '\n'])

            hotel_id = hotel['id']
            url = f'https://hotels.com/ho{hotel_id}'
            message = ''.join([message, 'Ссылка на сайт: ', url, '\n'])

            messages.append([hotel_id, message])
        return messages
    except (KeyError, TypeError) as exc:
        make_log(lvl='error', text=f'low or high price message {exc}')
        return None
