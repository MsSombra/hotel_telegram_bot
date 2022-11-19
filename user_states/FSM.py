from telebot.handler_backends import State, StatesGroup


# Создаем состояния пользователя для последовательности вопросов
class UserInfoState(StatesGroup):
    city = State()
    clarify_city = State()
    price_min = State()
    price_max = State()
    distance_max = State()
    hotels_amount = State()
    photos_need = State()
    photos_amount = State()
