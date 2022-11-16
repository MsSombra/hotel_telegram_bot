import logging


def make_log(lvl: str, text: str):
    """
    Функция для импорта в другие файлы, делает записи логов в консоль и файл log_func.log
    :param lvl: передается уровень сообщения лога
    :param text: передается текст сообщения лога
    :return: сообщение лога выводится в консоль и записывается в файл
    """
    file_log = logging.FileHandler(f'{__name__}.log')
    console_out = logging.StreamHandler()

    logging.basicConfig(handlers=(file_log, console_out),
                        format='[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S',
                        level=logging.INFO)

    if lvl == 'debag':
        logging.debug(f"A DEBUG Message | {text}")
    elif lvl == 'info':
        logging.info(f"An INFO | {text}")
    elif lvl == 'warning':
        logging.warning(f"A WARNING | {text}")
    elif lvl == 'error':
        logging.error(f"An ERROR | {text}")
    elif lvl == 'critical':
        logging.critical(f"A message of CRITICAL severity | {text}")