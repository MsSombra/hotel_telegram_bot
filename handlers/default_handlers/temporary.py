from telebot.types import Message
from loader import bot
from log_func import make_log
from media.send_media import one_animation


@bot.message_handler(commands=['history'])
def other_commands_reply(message: Message) -> None:
    """ Используется для ответа на вызов команд, которые не сделаны. """
    make_log(lvl='info', text=f'temporary command worked for chat_id {message.chat.id}')

    one_animation(message=message, file_name='pony.gif')

    reply_text = '...Находится в разработке...'
    bot.send_message(message.chat.id, reply_text)
