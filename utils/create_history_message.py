from log_func import make_log
from database.db_for_history import UserReq


def make_history_message(user_id: str) -> list:
    """ Функция запрашивает данные из БД users_history и собирает данные от user_id в список сообщений. """
    make_log(lvl='info', text=f'making history message for user {user_id}')

    messages = list()
    for info in UserReq.select().where(UserReq.user_id == user_id):
        message = ''.join([f'Выбранная команда: {info.command}\n',
                           f'Дата и время запроса: {info.date.strftime("%Y.%m.%d, %H:%M ")}\n',
                           f'Город поиска: {info.city}\n',
                           'Найденные отели: \n'])

        if info.request:
            for hotel in info.request:
                message = ''.join([message, '*' * 15, '\n', hotel.text_message, '\n'])
        else:
            message = ''.join([message, '\n', 'Запрос не дал результатов.'])

        messages.append(message)

    return messages
