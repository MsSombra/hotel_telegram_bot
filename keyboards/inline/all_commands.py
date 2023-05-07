from log_func import make_log
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def commands_markup() -> InlineKeyboardMarkup:
    """ Создает клавиатуру с кнопками для имеющихся команд"""

    markup_inline = InlineKeyboardMarkup(row_width=1)
    btn_help = InlineKeyboardButton(text="/help", callback_data="/help")
    btn_lowprice = InlineKeyboardButton(text="/lowprice", callback_data="/lowprice")
    btn_highprice = InlineKeyboardButton(text="/highprice", callback_data="/highprice")
    btn_bestdeal = InlineKeyboardButton(text="/bestdeal", callback_data="/bestdeal")

    markup_inline.add(btn_help, btn_lowprice, btn_highprice, btn_bestdeal)
    make_log(lvl='info', text="(func: commands_markup): commands markup made")
    return markup_inline
