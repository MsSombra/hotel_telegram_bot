import datetime
from log_func import make_log


def calculate_days(checkin_date: str, checkout_date: str) -> int:
    """ Считает количество дней пребывания в отеле. """
    make_log(lvl='info', text='period calculated')

    pattern = '%Y-%m-%d'
    day_1 = datetime.datetime.strptime(checkin_date, pattern)
    day_2 = datetime.datetime.strptime(checkout_date, pattern)
    result = day_2 - day_1
    number_days = result.days
    return number_days
