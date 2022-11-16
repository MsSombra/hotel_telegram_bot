def change_language_date(text: str) -> str:
    """ Находит и меняет в тексте слова year, month, day на год, месяц и день. """
    words = {'year': 'год', 'month': 'месяц', 'day': 'день'}
    for date in words.keys():
        if text.find(date) != -1:
            new_text = text.replace(date, words[date])
            return new_text
