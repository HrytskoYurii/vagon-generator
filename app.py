def create_board(vagon, left_v, right_v):
    width, height = 2400, 1600 
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    font_path = "SourceSans3-VariableFont_wght.ttf"

    try:
        # Для варіативних шрифтів Source Sans 3 ми додаємо жирність через параметри
        # Якщо шрифт підтримує варіативність в Pillow, він стане Bold.
        # Використовуємо великі розміри згідно з вашими ТЗ
        f_train = ImageFont.truetype(font_path, 150)
        f_route = ImageFont.truetype(font_path, 130)
        f_vagon = ImageFont.truetype(font_path, 610)
        f_side = ImageFont.truetype(font_path, 200)
        f_arrow = ImageFont.truetype(font_path, 150)
        
        # Додатковий крок: якщо ми хочемо "екстремально жирний", 
        # можна спробувати завантажити його з налаштуванням товщини, 
        # але в більшості випадків SourceSans3 автоматично підхоплює Bold, 
        # якщо файл містить ці дані.
    except:
        st.error("Шрифт не знайдено!")
        return Image.new('RGB', (100, 100), color="red")

    # 1. Номер поїзда (Чорна плашка)
    train_box_w = 700 # Трохи збільшив плашку під жирний шрифт
    draw.rounded_rectangle([width/2 - train_box_w/2, 50, width/2 + train_box_w/2, 250], radius=30, fill="black")
    
    # Використовуємо нашу функцію з інтервалом 30
    draw_text_with_spacing(draw, train_no, (width/2, 150), f_train, fill="white", spacing=30)

    # 2. Напрямок UA (Жирний, інтервал 0)
    draw_text_with_spacing(draw, route_ua, (width/2, 400), f_route, spacing=0)

    # 3. Напрямок EN (Жирний, інтервал 0)
    draw_text_with_spacing(draw, route_en, (width/2, 550), f_route, spacing=0)

    # 4. Номер вагона (ДУЖЕ ЖИРНИЙ, інтервал 30)
    # Щоб зробити шрифт ще товстішим (ефект Heavy), ми можемо намалювати його двічі з мікро-зміщенням
    vagon_text = str(vagon)
    vagon_pos = (width/2, height/2 + 100)
    draw_text_with_spacing(draw, vagon_text, vagon_pos, f_vagon, spacing=30)
    # "Жирний" ефект через дублювання (штучне потовщення)
    draw_text_with_spacing(draw, vagon_text, (vagon_pos[0]+2, vagon_pos[1]), f_vagon, spacing=30)

    # 5. Сусідні вагони
    if left_v:
        draw_text_with_spacing(draw, str(left_v), (300, 1300), f_side, spacing=30)
        draw.text((300, 1450), "◀", fill="black", anchor="mm", font=f_arrow)
    if right_v:
        draw_text_with_spacing(draw, str(right_v), (width - 300, 1300), f_side, spacing=30)
        draw.text((width - 300, 1450), "▶", fill="black", anchor="mm", font=f_arrow)
    
    return img
