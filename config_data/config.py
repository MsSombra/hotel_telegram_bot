import os

from dotenv import find_dotenv, load_dotenv

# проверяем наличие файла .env и загружаем из него данные
if not load_dotenv(find_dotenv()):
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
