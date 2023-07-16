from logging_func import logger
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def commands_markup() -> InlineKeyboardMarkup:
    """ Создает клавиатуру с кнопками для имеющихся команд"""

    markup_inline = InlineKeyboardMarkup(row_width=1)
    btn_help = InlineKeyboardButton(text="/help", callback_data="/help")
    btn_lowprice = InlineKeyboardButton(text="/lowprice", callback_data="/lowprice")
    btn_highprice = InlineKeyboardButton(text="/highprice", callback_data="/highprice")
    btn_bestdeal = InlineKeyboardButton(text="/bestdeal", callback_data="/bestdeal")

    markup_inline.add(btn_help, btn_lowprice, btn_highprice, btn_bestdeal)
    logger.info("commands markup made")
    return markup_inline
