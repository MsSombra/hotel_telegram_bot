from log_func import make_log


def make_photo_url(photo_number: int, photo_data: dict) -> list:
    """Проходит по словарю и возвращает список из строк со ссылками на фотографии в количестве photo_number"""
    make_log(lvl='info', text='(func: making_photos_url): start working')

    photos_url = []
    for number in range(photo_number):
        try:
            new_photo = photo_data['hotelImages'][number]['baseUrl']
            new_photo_url = new_photo.format(size=photo_data['hotelImages'][number]['sizes'][0]['suffix'])
        except KeyError:
            make_log(lvl='error', text='(func: making_photos_url) - KeyError')
            return None
        photos_url.append(new_photo_url)

    make_log(lvl='info', text='(func: making_photos_url): end working')
    return photos_url
