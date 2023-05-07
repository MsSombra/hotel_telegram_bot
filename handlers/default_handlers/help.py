from loader import bot
from log_func import make_log
from media.send_media import one_photo
from telebot.types import Message


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    """ Команда help. Отправляет пользователю пояснения имеющихся команд. """
    make_log(lvl='info', text=f'help command reply worked for chat_id {message.chat.id}')

    one_photo(message=message, file_name='Gorlum.png')

    reply_help = 'Моя прелесть знает перевод с эльфийского.\n' \
                 'Все команды с кратким пояснением можно посмотреть по кнопке Меню в левом нижнем углу.' \
                 'Также их можно записывать самостоятельно или выбирать по кнопке в приветственном сообщении.\n' \
                 '/start - вызывает приветственное сообщение с командами-кнопками.\n' \
                 '/help - вызывает меня.\n' \
                 '/lowprice - поиск самых дешевых отелей в выбранном городе.\n' \
                 '/highprice - поиск самых дорогих отелей в выбранном городе.\n' \
                 '/bestdeal - поиск отелей по заданному диапазону цен и расстоянию от центра выбранного города.\n' \
                 'При поиске отелей указывается количество отелей, которое бот покажет, ' \
                 'также можно запросить фото и указать их количество.\n' \
                 '/history - показывает историю запросов и их результат (найденные отели)\n'
    bot.send_message(message.chat.id, reply_help)
