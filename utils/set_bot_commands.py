from telebot.types import BotCommand

from loader import bot


def set_all_commands():
    """ Устанавливает команды бота с описанием. """
    bot.set_my_commands([
        BotCommand(command="/start", description="Вступительное сообщение"),
        BotCommand(command="/help", description="Пояснение команд"),
        BotCommand(command="/lowprice", description="Топ самых дешевых отелей"),
        BotCommand(command="/highprice", description="Топ самых дорогих отелей"),
        BotCommand(command="/bestdeal", description="Лучшие по цене и расположению"),
        BotCommand(command="/history", description="История поиска")
    ])
