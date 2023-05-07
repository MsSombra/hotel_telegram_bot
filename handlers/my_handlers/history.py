from loader import bot
from log_func import make_log
from telebot.types import Message
from utils.create_history_message import make_history_message


@bot.message_handler(commands=['history'])
def history_reply(message: Message) -> None:
    """ Обрабатывает команду /history. Отправляет сообщение с данными, полученными от базы данных. """
    make_log(lvl='info', text=f'(func: history_reply): history command reply worked for chat_id {message.chat.id}')

    messages = make_history_message(str(message.from_user.id))
    for text in messages:
        bot.send_message(message.from_user.id, text)

