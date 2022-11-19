from telebot.types import Message
from loader import bot
from handlers import default_handlers, my_handlers
from keyboards.inline import all_commands
from log_func import make_log
from media.send_media import one_photo


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """ Команда start. Отправляет пользователю приветственное сообщение и кнопки с командами. """
    make_log(lvl='info', text='start command worked')

    one_photo(message=message, file_name='Barlyman.png')

    reply_start = 'Приветствую в таверне "Гарцующий пони", путник! Мы помогаем с поиском отелей под ваши запросы.' \
                  'Ниже представлен список наших услуг.'
    bot.send_message(message.chat.id, reply_start)

    bot.send_message(message.chat.id, text='Услуги:', reply_markup=all_commands.commands_markup())


@bot.callback_query_handler(func=lambda call: call.data in ['/help', '/lowprice', '/highprice', '/bestdeal'])
def callback_inline(call):
    """ Обрабатывает нажатие кнопок с командами бота. """

    if call.message:
        make_log(lvl='info', text=f'callback for inline commands worked for chat_id {call.message.chat.id}')

        if call.data == '/help':
            default_handlers.help.bot_help(call.message)
        elif call.data == '/lowprice':
            my_handlers.low_and_high.lowprice(call.message)
        elif call.data == '/highprice':
            my_handlers.low_and_high.highprice(call.message)
        elif call.data == '/bestdeal':
            my_handlers.bestdeal.bestdeal_reply(call.message)
