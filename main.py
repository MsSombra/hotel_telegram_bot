from loader import bot
from telebot.custom_filters import StateFilter
import handlers
from utils.set_bot_commands import set_all_commands
from log_func import make_log


if __name__ == '__main__':
    make_log(lvl='info', text='bot started')
    bot.add_custom_filter(StateFilter(bot))
    set_all_commands()
    bot.polling(none_stop=True)

