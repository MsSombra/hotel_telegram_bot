from telebot.custom_filters import StateFilter

import handlers
from loader import bot
from logging_func import logger, logging_config
from utils.set_bot_commands import set_all_commands

if __name__ == '__main__':
    logging_config()
    logger.info('bot started')
    bot.add_custom_filter(StateFilter(bot))
    set_all_commands()
    bot.polling(none_stop=True)
