from database.db_for_history import UserReq
from logging_func import logger


def make_history_message(user_id: str) -> list:
    """ Функция запрашивает данные из БД users_history и собирает данные от user_id в список сообщений. """
    logger.info(f'start for user {user_id}')

    messages = list()
    query = UserReq.select().where(UserReq.user_id == user_id)
    if query:
        for info in query:
            message = ''.join([f'Выбранная команда: {info.command}\n',
                               f'Дата и время запроса: {info.date.strftime("%Y.%m.%d, %H:%M ")}\n',
                               f'Город поиска: {info.city}\n',
                               'Найденные отели: \n'])

            if info.request:
                for hotel in info.request:
                    message = ''.join([message, '\n', hotel.text_message, '\n'])
            else:
                message = ''.join([message, '\n', 'Запрос не дал результатов.'])

            messages.append(message)

    else:
        message = 'Ваша история поиска пока что пуста.'
        messages.append(message)

    logger.info(f'end for user {user_id}')
    return messages
