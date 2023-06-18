from log_func import make_log
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def yes_or_no() -> InlineKeyboardMarkup:
    """ Клавиатура для выбора 'да' или 'нет'. """

    keyboard = InlineKeyboardMarkup()
    key_yes = InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)

    make_log(lvl="info", text="(func: yes_or_no): yes or no markup made")
    return keyboard
