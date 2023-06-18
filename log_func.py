import logging


def make_log(lvl: str, text: str):
    """
    Функция для импорта в другие файлы, делает записи логов в консоль и файл log_func.log
    :param lvl: передается уровень сообщения лога
    :param text: передается текст сообщения лога
    :return: сообщение лога выводится в консоль и записывается в файл
    """
    file = logging.FileHandler('log_file.log')
    console_out = logging.StreamHandler()

    logging.basicConfig(handlers=(file, console_out),
                        format='[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S',
                        level=logging.DEBUG,
                        encoding='utf-8')

    if lvl == 'debag':
        logging.debug(f"{text}")
    elif lvl == 'info':
        logging.info(f"{text}")
    elif lvl == 'warning':
        logging.warning(f"{text}")
    elif lvl == 'error':
        logging.error(f"{text}")
    elif lvl == 'critical':
        logging.critical(f"{text}")
