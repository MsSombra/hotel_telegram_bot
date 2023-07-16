from logging_func import logger
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def yes_or_no() -> InlineKeyboardMarkup:
    """ Клавиатура для выбора 'да' или 'нет'. """

    keyboard = InlineKeyboardMarkup()
    key_yes = InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)

    logger.info("yes or no markup made")
    return keyboard
