def get_image_hash_bypath(filepath: str, size: int, color_format: str = 'bnw'):
    """
        Генерация перцептивного хэша изображения по пути в файловой системе
        args:
            filepath: путь до файла
            size: размер сжатия изображения - >= 4 и должна быть одной из степени 2
            color_format: 
                            'bnw' - Ч/Б формат
                            'grs' - Оттенки серого
                            'RGB' - Цветной формат
        returns:
            bytearray(bytea) - Перцептивный хэш
            None(NULL) - Если файл не существует
            0 - Ошибка чтения файла
    """

    # Проверка на корректный путь до файла
    import os
    if not os.path.exists(filepath): 
        # Если не существует -- вернуть None(NULL)
        return None

    # Импорт модулей
    import io
    from PIL import Image

    # Настройка параметров формата хэша:
    #   1. color_format - формат цвета
    #   2. color_format_to_write - байтовое значение формата для записи в первые 2 байта хэша
    if color_format == 'bnw':
        color_format = '1'
        color_format_to_write = int(1).to_bytes(2, byteorder="little")
    elif color_format == 'grs':
        color_format = 'L'
        color_format_to_write = int(2).to_bytes(2, byteorder="little")
    elif color_format == 'rgb':
        color_format = 'RGB'
        color_format_to_write = int(3).to_bytes(2, byteorder="little")
    else:
        color_format = '1'
        color_format_to_write = int(1).to_bytes(2, byteorder="little")

    # Загрузка файла
    with open(filepath, 'rb') as fr:
        try:
            img_to_analize = Image.open(                      # 3. Create Image object
                                    io.BytesIO(               # 2. Create BytesIO format
                                            fr.read()         # 1. Read file
                                            )
                                    ).resize((size, size)     # 4. Resize Image
                                ).convert(color_format)       # 5. Convert to color format
        except:
            return 0
    
    # Загрузка первого пикселя для анализа
    #   Если указан формат Ч/Б или оттенки серого - 
    #       будет всего 1 значения интенсивности цвета на пиксель
    #       и такое значение нужно укомпоновать в список - в целях однотипности переменных
    #   Если указан цветной формат - пропустить шаг, т.к.
    #       для такого пикселя уже будет список 3 значений интенсивности:
    #       для красного, зеленого и синего
    first_pixel_val = img_to_analize.getpixel((0,0))
    if first_pixel_val.__class__ == int:
        first_pixel_val = [first_pixel_val]

    # Нахождение среднего значения интенсивности для каждого типа интенсивности
    avg_val = [0 for _ in first_pixel_val]
    for i in range(size):
        for j in range(size):

            pixel_val_rgb = img_to_analize.getpixel((i,j))
            if pixel_val_rgb.__class__ == int: 
                pixel_val_rgb = [pixel_val_rgb]
            for k, val in enumerate(pixel_val_rgb):
                avg_val[k] += val

    for n in range(len(avg_val)):         
        avg_val[n] /= size ** 2

    # Запись в первые 2 байта служебной информации
    values = [color_format_to_write, '']
    # Двойной цикл по каждому пикселю изображения
    for i in range(size):
        for j in range(size):
            pixel_val_rgb = img_to_analize.getpixel((i,j))
            if pixel_val_rgb.__class__ == int: 
                pixel_val_rgb = [pixel_val_rgb]
            
            # Цикл по каждому значению интенсивности пикселя
            for n, pixel_val in enumerate(pixel_val_rgb):
                # Сравнение интенсивности пискеля с соответствующим значением средней интенсивности
                #   и создание бита 1/0
                if pixel_val >= avg_val[n]:
                    k = '1'
                else:
                    k = '0'

                # Если длина последнего элемента списка равна 8 - перевод битов в байты
                #   и внесение нового бита в отлельный элемент
                if len(values[-1]) == 8:
                    values[-1] = int(values[-1], 2).to_bytes(2, byteorder="little")
                    values.append(k)
                else: 
                    # Иначе - дополнение последнего элемента новым битом
                    values[-1] += k

    # Генерация байтов из последних необработанных битов
    values[-1] = int(values[-1], 2).to_bytes(2, byteorder="little")

    # Возврат 1 элемента bytearray из списка составленных элементов bytes
    return bytearray(b''.join(values))


def get_image_hash_byurl(url: str, size: int, color_format: str = 'bnw'):
    """
        Генерация перцептивного хэша изображения по простому url
        args:
            url: ссылка на файл
            size: размер сжатия изображения - >= 4 и должна быть одной из степени 2
            color_format: 
                            'bnw' - Ч/Б формат
                            'grs' - Оттенки серого
                            'RGB' - Цветной формат
        returns:
            bytearray(bytea) - Перцептивный хэш
            None(NULL) - Если файл не существует
            0 - Ошибка чтения файла
    """

    # Импорт модулей
    import io
    from requests import get
    from PIL import Image

    # Настройка параметров формата хэша:
    #   1. color_format - формат цвета
    #   2. color_format_to_write - байтовое значение формата для записи в первые 2 байта хэша
    if color_format == 'bnw':
        color_format = '1'
        color_format_to_write = int(1).to_bytes(2, byteorder="little")
    elif color_format == 'grs':
        color_format = 'L'
        color_format_to_write = int(2).to_bytes(2, byteorder="little")
    elif color_format == 'rgb':
        color_format = 'RGB'
        color_format_to_write = int(3).to_bytes(2, byteorder="little")
    else:
        color_format = '1'
        color_format_to_write = int(1).to_bytes(2, byteorder="little")

    # Загрузка файла
    try:
        response = get(url)
        img_to_analize = Image.open(                      # 3. Create Image object
                                io.BytesIO(               # 2. Create BytesIO format
                                        response.content  # 1. Read file
                                        )
                                ).resize((size, size)     # 4. Resize Image
                            ).convert(color_format)       # 5. Convert to color format
    except:
        return 0
    
    # Загрузка первого пикселя для анализа
    #   Если указан формат Ч/Б или оттенки серого - 
    #       будет всего 1 значения интенсивности цвета на пиксель
    #       и такое значение нужно укомпоновать в список - в целях однотипности переменных
    #   Если указан цветной формат - пропустить шаг, т.к.
    #       для такого пикселя уже будет список 3 значений интенсивности:
    #       для красного, зеленого и синего
    first_pixel_val = img_to_analize.getpixel((0,0))
    if first_pixel_val.__class__ == int:
        first_pixel_val = [first_pixel_val]

    # Нахождение среднего значения интенсивности для каждого типа интенсивности
    avg_val = [0 for _ in first_pixel_val]
    for i in range(size):
        for j in range(size):

            pixel_val_rgb = img_to_analize.getpixel((i,j))
            if pixel_val_rgb.__class__ == int: 
                pixel_val_rgb = [pixel_val_rgb]
            for k, val in enumerate(pixel_val_rgb):
                avg_val[k] += val

    for n in range(len(avg_val)):         
        avg_val[n] /= size ** 2

    # Запись в первые 2 байта служебной информации
    values = [color_format_to_write, '']
    # Двойной цикл по каждому пикселю изображения
    for i in range(size):
        for j in range(size):
            pixel_val_rgb = img_to_analize.getpixel((i,j))
            if pixel_val_rgb.__class__ == int: 
                pixel_val_rgb = [pixel_val_rgb]
            
            # Цикл по каждому значению интенсивности пикселя
            for n, pixel_val in enumerate(pixel_val_rgb):
                # Сравнение интенсивности пискеля с соответствующим значением средней интенсивности
                #   и создание бита 1/0
                if pixel_val >= avg_val[n]:
                    k = '1'
                else:
                    k = '0'

                # Если длина последнего элемента списка равна 8 - перевод битов в байты
                #   и внесение нового бита в отлельный элемент
                if len(values[-1]) == 8:
                    values[-1] = int(values[-1], 2).to_bytes(2, byteorder="little")
                    values.append(k)
                else: 
                    # Иначе - дополнение последнего элемента новым битом
                    values[-1] += k

    # Генерация байтов из последних необработанных битов
    values[-1] = int(values[-1], 2).to_bytes(2, byteorder="little")

    # Возврат 1 элемента bytearray из списка составленных элементов bytes
    return bytearray(b''.join(values))


def get_image_hash_byrequest(domain: str, qpath:str, method: str, payload:str, schema:str, size: int, color_format: str = 'bnw'):
    """
        Генерация перцептивного хэша изображения по сложносоставному запросу
        args:
            domain: доменное имя
            qpath: путь ссылки
            method: метод запроса - GET/POST
            payload: полезнаая нагрузка запроса
            schema: http/https/ws
            size: размер сжатия изображения - >= 4 и должна быть одной из степени 2
            color_format: 
                            'bnw' - Ч/Б формат
                            'grs' - Оттенки серого
                            'RGB' - Цветной формат
        returns:
            bytearray(bytea) - Перцептивный хэш
            None(NULL) - Если файл не существует
            0 - Ошибка чтения файла
    """

    # Импорт модулей
    import io
    from requests import request
    from PIL import Image

    # Настройка параметров формата хэша:
    #   1. color_format - формат цвета
    #   2. color_format_to_write - байтовое значение формата для записи в первые 2 байта хэша
    if color_format == 'bnw':
        color_format = '1'
        color_format_to_write = int(1).to_bytes(2, byteorder="little")
    elif color_format == 'grs':
        color_format = 'L'
        color_format_to_write = int(2).to_bytes(2, byteorder="little")
    elif color_format == 'rgb':
        color_format = 'RGB'
        color_format_to_write = int(3).to_bytes(2, byteorder="little")
    else:
        color_format = '1'
        color_format_to_write = int(1).to_bytes(2, byteorder="little")

    # Загрузка файла
    try:
        if payload != '':
            response = request(
                url=f"{schema}://{domain}/{qpath}",
                method=method,
                payload=payload
            )
        else:
            response = request(
                url=f"{schema}://{domain}/{qpath}",
                method=method
            )
        img_to_analize = Image.open(                      # 3. Create Image object
                                io.BytesIO(               # 2. Create BytesIO format
                                        response.content  # 1. Read file
                                        )
                                ).resize((size, size)     # 4. Resize Image
                            ).convert(color_format)       # 5. Convert to color format
    except:
        return 0
    
    # Загрузка первого пикселя для анализа
    #   Если указан формат Ч/Б или оттенки серого - 
    #       будет всего 1 значения интенсивности цвета на пиксель
    #       и такое значение нужно укомпоновать в список - в целях однотипности переменных
    #   Если указан цветной формат - пропустить шаг, т.к.
    #       для такого пикселя уже будет список 3 значений интенсивности:
    #       для красного, зеленого и синего
    first_pixel_val = img_to_analize.getpixel((0,0))
    if first_pixel_val.__class__ == int:
        first_pixel_val = [first_pixel_val]

    # Нахождение среднего значения интенсивности для каждого типа интенсивности
    avg_val = [0 for _ in first_pixel_val]
    for i in range(size):
        for j in range(size):

            pixel_val_rgb = img_to_analize.getpixel((i,j))
            if pixel_val_rgb.__class__ == int: 
                pixel_val_rgb = [pixel_val_rgb]
            for k, val in enumerate(pixel_val_rgb):
                avg_val[k] += val

    for n in range(len(avg_val)):         
        avg_val[n] /= size ** 2

    # Запись в первые 2 байта служебной информации
    values = [color_format_to_write, '']
    # Двойной цикл по каждому пикселю изображения
    for i in range(size):
        for j in range(size):
            pixel_val_rgb = img_to_analize.getpixel((i,j))
            if pixel_val_rgb.__class__ == int: 
                pixel_val_rgb = [pixel_val_rgb]
            
            # Цикл по каждому значению интенсивности пикселя
            for n, pixel_val in enumerate(pixel_val_rgb):
                # Сравнение интенсивности пискеля с соответствующим значением средней интенсивности
                #   и создание бита 1/0
                if pixel_val >= avg_val[n]:
                    k = '1'
                else:
                    k = '0'

                # Если длина последнего элемента списка равна 8 - перевод битов в байты
                #   и внесение нового бита в отлельный элемент
                if len(values[-1]) == 8:
                    values[-1] = int(values[-1], 2).to_bytes(2, byteorder="little")
                    values.append(k)
                else: 
                    # Иначе - дополнение последнего элемента новым битом
                    values[-1] += k

    # Генерация байтов из последних необработанных битов
    values[-1] = int(values[-1], 2).to_bytes(2, byteorder="little")

    # Возврат 1 элемента bytearray из списка составленных элементов bytes
    return bytearray(b''.join(values))


def get_image_hash_bybase64(base64str: str, size: int, color_format: str = 'bnw'):
    """
        Генерация перцептивного хэша изображения из base64
        args:
            base64str: строка изображения в base64
            size: размер сжатия изображения - >= 4 и должна быть одной из степени 2
            color_format: 
                            'bnw' - Ч/Б формат
                            'grs' - Оттенки серого
                            'RGB' - Цветной формат
        returns:
            bytearray(bytea) - Перцептивный хэш
            None(NULL) - Если файл не существует
            0 - Ошибка чтения файла
    """

    # Импорт модулей
    import io
    from base64 import b64decode
    from PIL import Image

    # Настройка параметров формата хэша:
    #   1. color_format - формат цвета
    #   2. color_format_to_write - байтовое значение формата для записи в первые 2 байта хэша
    if color_format == 'bnw':
        color_format = '1'
        color_format_to_write = int(1).to_bytes(2, byteorder="little")
    elif color_format == 'grs':
        color_format = 'L'
        color_format_to_write = int(2).to_bytes(2, byteorder="little")
    elif color_format == 'rgb':
        color_format = 'RGB'
        color_format_to_write = int(3).to_bytes(2, byteorder="little")
    else:
        color_format = '1'
        color_format_to_write = int(1).to_bytes(2, byteorder="little")

    # Загрузка файла
    try:
        img_to_analize = Image.open(                            # 3. Create Image object
                                io.BytesIO(                     # 2. Create BytesIO format
                                        b64decode(base64str)    # 1. Read file
                                        )
                                ).resize((size, size)           # 4. Resize Image
                            ).convert(color_format)             # 5. Convert to color format
    except:
        return 0
    
    # Загрузка первого пикселя для анализа
    #   Если указан формат Ч/Б или оттенки серого - 
    #       будет всего 1 значения интенсивности цвета на пиксель
    #       и такое значение нужно укомпоновать в список - в целях однотипности переменных
    #   Если указан цветной формат - пропустить шаг, т.к.
    #       для такого пикселя уже будет список 3 значений интенсивности:
    #       для красного, зеленого и синего
    first_pixel_val = img_to_analize.getpixel((0,0))
    if first_pixel_val.__class__ == int:
        first_pixel_val = [first_pixel_val]

    # Нахождение среднего значения интенсивности для каждого типа интенсивности
    avg_val = [0 for _ in first_pixel_val]
    for i in range(size):
        for j in range(size):

            pixel_val_rgb = img_to_analize.getpixel((i,j))
            if pixel_val_rgb.__class__ == int: 
                pixel_val_rgb = [pixel_val_rgb]
            for k, val in enumerate(pixel_val_rgb):
                avg_val[k] += val

    for n in range(len(avg_val)):         
        avg_val[n] /= size ** 2

    # Запись в первые 2 байта служебной информации
    values = [color_format_to_write, '']
    # Двойной цикл по каждому пикселю изображения
    for i in range(size):
        for j in range(size):
            pixel_val_rgb = img_to_analize.getpixel((i,j))
            if pixel_val_rgb.__class__ == int: 
                pixel_val_rgb = [pixel_val_rgb]
            
            # Цикл по каждому значению интенсивности пикселя
            for n, pixel_val in enumerate(pixel_val_rgb):
                # Сравнение интенсивности пискеля с соответствующим значением средней интенсивности
                #   и создание бита 1/0
                if pixel_val >= avg_val[n]:
                    k = '1'
                else:
                    k = '0'

                # Если длина последнего элемента списка равна 8 - перевод битов в байты
                #   и внесение нового бита в отлельный элемент
                if len(values[-1]) == 8:
                    values[-1] = int(values[-1], 2).to_bytes(2, byteorder="little")
                    values.append(k)
                else: 
                    # Иначе - дополнение последнего элемента новым битом
                    values[-1] += k

    # Генерация байтов из последних необработанных битов
    values[-1] = int(values[-1], 2).to_bytes(2, byteorder="little")

    # Возврат 1 элемента bytearray из списка составленных элементов bytes
    return bytearray(b''.join(values))


def get_simple_hamming_distance(a: bytearray, b:bytearray):
    """
        Нахождение простого расстояния Хэмминга для двух хэшей
        args:
            a - bytearray 1
            b - bytearray 2
        returns:
            -2 - для ошибки разных форматов хэшей
            -1 - для ошибки размерности хэшей
            значение от 0 до 100 - где:
                                        0 - разные изображения
                                        100 - одинаковые изображения
    """

    # Проверка на форматы хэшей
    if a[0:2] != b[0:2]: return -2

    # Проверка на размерность хэшей
    count_vals = len(a) - 2
    if count_vals != len(b) - 2: return -1

    # Счетчик совпавших байт
    matched_vals = 0

    # Цикл сравнения байт
    for i in range(count_vals, 2):
        if a[i] == b[i]:
            matched_vals += 1

    # Возврат рейтинга совпадения
    return (matched_vals / count_vals) * 100


def get_detail_hamming_distance(a: bytearray, b:bytearray):
    """
        Нахождение точного расстояния Хэмминга для двух хэшей
        args:
            a - bytearray 1
            b - bytearray 2
        returns:
            -2 - для ошибки разных форматов хэшей
            -1 - для ошибки размерности хэшей
            значение от 0 до 100 - где:
                                        0 - разные изображения
                                        100 - одинаковые изображения
    """

    # Проверка на форматы хэшей
    if a[0:2] != b[0:2]: return -2
    
    # Проверка на размерность хэшей
    count_vals = len(a)
    if count_vals != len(b): return -1

    # Текущая разница изображений
    current_diff = 0

    # Максимальная разница изображений
    total_diff = count_vals * 255

    # Цикл по сравнению битов
    for i in range(count_vals-2):
        current_diff += abs(a[i+2] - b[i+2])

    # Возврат рейтинга совпадения
    return 100 - (current_diff / total_diff) * 100


def get_base64_bypath(path: str):
    """
        Получение base64 изображения по пути в файловой директории
    """

    # Проверка существования файла
    from os.path import exists
    if not exists(path): return -2

    from base64 import b64encode

    # Открытие и возврат base64
    with open(path, 'rb') as fr:
        return b64encode(fr.read())


def get_base64_byurl(url: str):
    """
        Получение base64 изображения по простому url
    """

    from base64 import b64encode
    from requests import get

    try:
        response = get(url)
        return b64encode(response.content)
    except:
        return -2


def get_base64_byrequest(domain: str, qpath:str, method: str, payload:str, schema:str):
    """
        Получение base64 изображения по сложносоставному запросу
    """

    from base64 import b64encode
    from requests import request
    
    try:
        if payload != '':
            response = request(
                url=f"{schema}://{domain}/{qpath}",
                method=method,
                payload=payload
            )
        else:
            response = request(
                url=f"{schema}://{domain}/{qpath}",
                method=method
            )

        return b64encode(response.content)
    except:
        return -2

