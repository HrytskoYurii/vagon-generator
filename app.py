def create_board(vagon, left_v, right_v):
    width, height = 1000, 700
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Вказуємо назву вашого завантаженого файлу
    font_path = "SourceSans3-VariableFont_wght.ttf" 

    try:
        # Спроба завантажити ваш шрифт
        f_train = ImageFont.truetype(font_path, 70)
        f_route = ImageFont.truetype(font_path, 90)
        f_main = ImageFont.truetype(font_path, 350)
        f_side = ImageFont.truetype(font_path, 120)
        f_arrow = ImageFont.truetype(font_path, 100) # Окремий розмір для стрілок
    except:
        # Якщо файл не знайдено (наприклад, помилка в назві), виведемо попередження
        st.error(f"Файл {font_path} не знайдено! Перевірте, чи завантажили ви його на GitHub.")
        f_train = f_route = f_main = f_side = f_arrow = ImageFont.load_default()

    # 1. Номер поїзда
    draw.rounded_rectangle([350, 20, 650, 130], radius=20, fill="black")
    draw.text((500, 75), train_no, fill="white", anchor="mm", font=f_train)

    # 2. Напрямок (UA та EN)
    draw.text((500, 210), route_ua, fill="black", anchor="mm", font=f_route)
    draw.text((500, 310), route_en, fill="black", anchor="mm", font=f_route)

    # 3. Номер вагона
    draw.text((500, 500), str(vagon), fill="black", anchor="mm", font=f_main)

    # 4. Сусідні вагони та стрілки
    if left_v:
        draw.text((150, 550), str(left_v), fill="black", anchor="mm", font=f_side)
        # Малюємо стрілку
        draw.text((150, 640), "◀", fill="black", anchor="mm", font=f_arrow)
    if right_v:
        draw.text((850, 550), str(right_v), fill="black", anchor="mm", font=f_side)
        # Малюємо стрілку
        draw.text((850, 640), "▶", fill="black", anchor="mm", font=f_arrow)
    
    return img
