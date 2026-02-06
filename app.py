import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

st.set_page_config(page_title="Vagon Board Gen", layout="centered")

st.title("🚉 Генератор маршрутних дощок")

# --- Ввід даних ---
with st.sidebar:
    st.header("⚙️ Налаштування")
    train_no = st.text_input("№ Поїзда", value="19/20")
    route_ua = st.text_input("Напрямок (UA)", value="Київ — Хелм")
    route_en = st.text_input("Напрямок (EN)", value="Kyiv — Chelm")
    
    col_v1, col_v2 = st.columns(2)
    start_v = col_v1.number_input("З вагона", min_value=1, value=14)
    end_v = col_v2.number_input("По вагон", min_value=1, value=16)

def create_board(vagon, left_v, right_v):
    width, height = 1000, 700
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Використовуємо твій шрифт
    font_path = "SourceSans3-VariableFont_wght.ttf" 

    try:
        f_train = ImageFont.truetype(font_path, 70)
        f_route = ImageFont.truetype(font_path, 90)
        f_main = ImageFont.truetype(font_path, 350)
        f_side = ImageFont.truetype(font_path, 120)
        f_arrow = ImageFont.truetype(font_path, 100)
    except:
        # Безпечний перехід на стандартний, якщо шрифту немає
        f_train = f_route = f_main = f_side = f_arrow = ImageFont.load_default()

    # 1. Номер поїзда
    draw.rounded_rectangle([350, 20, 650, 130], radius=20, fill="black")
    draw.text((500, 75), train_no, fill="white", anchor="mm", font=f_train)

    # 2. Напрямок
    draw.text((500, 210), route_ua, fill="black", anchor="mm", font=f_route)
    draw.text((500, 310), route_en, fill="black", anchor="mm", font=f_route)

    # 3. Номер вагона
    draw.text((500, 500), str(vagon), fill="black", anchor="mm", font=f_main)

    # 4. Сусідні вагони
    if left_v:
        draw.text((150, 550), str(left_v), fill="black", anchor="mm", font=f_side)
        draw.text((150, 640), "◀", fill="black", anchor="mm", font=f_arrow)
    if right_v:
        draw.text((850, 550), str(right_v), fill="black", anchor="mm", font=f_side)
        draw.text((850, 640), "▶", fill="black", anchor="mm", font=f_arrow)
    
    return img

# Кнопка генерації
if st.button("🚀 Згенерувати всі макети"):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for v in range(start_v, end_v + 1):
            p = v - 1 if v > start_v else None
            n = v + 1 if v < end_v else None
            
            # Створюємо обидва варіанти для кожного вагона
            img1 = create_board(v, p, n)
            img2 = create_board(v, n, p)
            
            # Зберігаємо в ZIP
            b1 = io.BytesIO(); img1.save(b1, format="PNG")
            zip_file.writestr(f"vagon_{v:02d}_side1.png", b1.getvalue())
            
            b2 = io.BytesIO(); img2.save(b2, format="PNG")
            zip_file.writestr(f"vagon_{v:02d}_side2.png", b2.getvalue())
            
            if v == start_v:
                st.image(img1, caption=f"Приклад макета для вагона {v}")

    st.download_button("📥 Завантажити ZIP з усіма макетами", zip_buffer.getvalue(), "boards.zip")
