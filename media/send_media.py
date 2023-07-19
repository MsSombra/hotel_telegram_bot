from telebot.types import InputMediaPhoto, Message

from loader import bot


def one_photo(message: Message, file_name: str) -> None:
    """ Отправляет одно фото по его названию """
    file = r'media/' + f'{file_name}'
    photo = open(file, 'rb')
    bot.send_photo(message.chat.id, photo)


def one_animation(message: Message, file_name: str) -> None:
    """ Отправляет одну гиф-анимацию по ее названию. """
    file = r'media/' + f'{file_name}'
    animation = open(file, 'rb')
    bot.send_animation(message.chat.id, animation)


def several_photos(message: Message, paths: list) -> None:
    """ Отправляет несколько фото по их ссылкам. """
    bot.send_media_group(message.chat.id, [InputMediaPhoto(path) for path in paths])
