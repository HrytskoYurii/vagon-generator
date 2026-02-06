import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

st.set_page_config(page_title="Vagon Board Gen Pro", layout="centered")

st.title("🚉 Професійний генератор дощок")

with st.sidebar:
    st.header("⚙️ Налаштування")
    train_no = st.text_input("№ Поїзда", value="19/20")
    route_ua = st.text_input("Напрямок (UA)", value="КИЇВ — ХЕЛМ")
    route_en = st.text_input("Напрямок (EN)", value="KYIV — CHELM")
    
    col_v1, col_v2 = st.columns(2)
    start_v = col_v1.number_input("З вагона", min_value=1, value=14)
    end_v = col_v2.number_input("По вагон", min_value=1, value=16)

# --- Функція для малювання тексту з інтервалами ---
def draw_text_with_spacing(draw, text, position, font, fill="black", spacing=0, anchor="mm"):
    # Розбиваємо текст на символи та рахуємо загальну ширину
    sum_width = sum(draw.textbbox((0, 0), char, font=font)[2] for char in text)
    total_width = sum_width + spacing * (len(text) - 1)
    
    # Визначаємо початкову точку X залежно від anchor
    x, y = position
    if anchor == "mm":
        current_x = x - total_width / 2
    elif anchor == "rm":
        current_x = x - total_width
    else: # lm
        current_x = x

    # Малюємо кожен символ окремо
    for char in text:
        draw.text((current_x, y), char, font=font, fill=fill, anchor="lm")
        char_width = draw.textbbox((0, 0), char, font=font)[2]
        current_x += char_width + spacing

def create_board(vagon, left_v, right_v):
    # Збільшуємо розмір полотна для високої якості (друк)
    width, height = 2400, 1600 
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    font_path = "SourceSans3-VariableFont_wght.ttf"

    try:
        # Встановлюємо розміри згідно з вашими вимогами
        f_train = ImageFont.truetype(font_path, 150)
        f_route = ImageFont.truetype(font_path, 130)
        f_vagon = ImageFont.truetype(font_path, 610)
        f_side = ImageFont.truetype(font_path, 200)
        f_arrow = ImageFont.truetype(font_path, 150)
    except:
        st.error("Шрифт не знайдено! Перевірте файл у репозиторії.")
        return Image.new('RGB', (100, 100), color="red")

    # 1. Номер поїзда (Чорна плашка + білий текст, інтервал 30)
    train_box_w = 600
    draw.rounded_rectangle([width/2 - train_box_w/2, 50, width/2 + train_box_w/2, 230], radius=30, fill="black")
    draw_text_with_spacing(draw, train_no, (width/2, 140), f_train, fill="white", spacing=30)

    # 2. Напрямок UA (інтервал 0)
    draw_text_with_spacing(draw, route_ua, (width/2, 380), f_route, spacing=0)

    # 3. Напрямок EN (інтервал 0)
    draw_text_with_spacing(draw, route_en, (width/2, 530), f_route, spacing=0)

    # 4. Номер вагона (інтервал 30)
    draw_text_with_spacing(draw, str(vagon), (width/2, height/2 + 150), f_vagon, spacing=30)

    # 5. Сусідні вагони (інтервал 30)
    if left_v:
        draw_text_with_spacing(draw, str(left_v), (300, 1300), f_side, spacing=30)
        draw.text((300, 1450), "◀", fill="black", anchor="mm", font=f_arrow)
    if right_v:
        draw_text_with_spacing(draw, str(right_v), (width - 300, 1300), f_side, spacing=30)
        draw.text((width - 300, 1450), "▶", fill="black", anchor="mm", font=f_arrow)
    
    return img

# Кнопки в інтерфейсі
if st.button("🚀 Згенерувати макети за вимогами"):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for v in range(start_v, end_v + 1):
            p, n = (v-1 if v > start_v else None), (v+1 if v < end_v else None)
            
            # Два варіанти (прямий і зворотний)
            sides = [(p, n, "side1"), (n, p, "side2")]
            for left, right, suffix in sides:
                img = create_board(v, left, right)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                zip_file.writestr(f"vagon_{v:02d}_{suffix}.png", buf.getvalue())
            
            if v == start_v:
                st.image(create_board(v, p, n), caption="Попередній перегляд (Варіант 1)")

    st.download_button("📥 Завантажити архів (ZIP)", zip_buffer.getvalue(), "boards_pro.zip")
