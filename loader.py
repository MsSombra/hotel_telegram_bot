from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config

# создаем бота для импорта в другие файлы
storage = StateMemoryStorage()
bot = TeleBot(token=config.TOKEN, state_storage=storage)

