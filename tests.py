import ImAnTool as imt

# Пути к 3 тестовым изображениям
img_path = 'source_img/a-let.jpg'                   # 1
img_colored_path = 'source_img/a-let_colored.jpg'   # 2
img_moved_path = 'source_img/a-let_moved.jpg'       # 3

# Ссылка на тестовое изображение
img_url = 'https://i.pinimg.com/originals/85/a3/10/85a31076a3e3777d48c205a369b3f674.png' # 4

# Данные для сложносоставного запроса на тестовое изображение 4
img_domain = 'i.pinimg.com'
img_qpath = 'originals/85/a3/10/85a31076a3e3777d48c205a369b3f674.png'
img_schema = 'https'
img_method = 'GET'
img_payload = ''

# Задание значений для хэширования
color_format = 'rgb'
zip_size = 32



""" Тестирование результатов """

# Хэширование по пути в файловой системе
a_1_hash = imt.get_image_hash_bypath(img_path, zip_size, color_format)

# Хэширование по получению base64 из изображения в файловой системе
a_2_b64 = imt.get_base64_bypath(img_colored_path)
a_2_hash = imt.get_image_hash_bybase64(a_2_b64, zip_size, color_format)

# Хэширование по url и сложносоставному запросу
a_4_hash = imt.get_image_hash_byurl(img_url, zip_size, color_format)
a_4_rhash = imt.get_image_hash_byrequest(   img_domain, 
                                            img_qpath, 
                                            img_method, 
                                            img_payload, 
                                            img_schema, 
                                            zip_size, 
                                            color_format
                                        )

# Хэширование по base64 из url
a_4_b64 = imt.get_base64_byurl(img_url)
a_4_b64_hash = imt.get_image_hash_bybase64(a_4_b64, zip_size, color_format)


a1_a2 = imt.get_simple_hamming_distance(a_1_hash, a_2_hash)
a1_a2_d = imt.get_detail_hamming_distance(a_1_hash, a_2_hash)
a2_a4 = imt.get_detail_hamming_distance(a_2_hash, a_4_hash)
a4r_a4b64h = imt.get_detail_hamming_distance(a_4_rhash, a_4_b64_hash)

print(f"Одинаковые изображения, разного цвета, простое расстояние, из разных источников: {a1_a2}")
print(f"Одинаковые изображения, разного цвета, детальное расстояние, из разных источников: {a1_a2_d}")
print(f"Похожие изображения, похожего цвета, детальное расстояние, из разных источников: {a2_a4}")
print(f"Одно и то же изображение, разные источники, детальное расстояние: {a4r_a4b64h}")
