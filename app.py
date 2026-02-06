import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
from googletrans import Translator

# Ініціалізація перекладача
translator = Translator()

st.set_page_config(page_title="Train Board Gen", layout="centered")

st.title("🚉 Генератор макетів за зразком")

# Ввід даних
with st.sidebar:
    st.header("⚙️ Налаштування")
    train_no = st.text_input("№ Поїзда", value="19/20")
    route_ua = st.text_input("Напрямок (UA)", value="Київ — Хелм")
    
    # Автоматичний переклад
    try:
        translated = translator.translate(route_ua, src='uk', dest='en').text
    except:
        translated = "Kyiv — Chelm"
    
    route_en = st.text_input("Напрямок (EN)", value=translated)
    
    c1, c2 = st.columns(2)
    start_v = c1.number_input("З вагона", min_value=1, value=14)
    end_v = c2.number_input("По вагон", min_value=1, value=16)

def create_image(vagon, left_v, right_v):
    width, height = 1000, 700
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Спрощена імітація шрифтів (якщо немає файлів ttf)
    try:
        f_train = ImageFont.load_default(size=60)
        f_route = ImageFont.load_default(size=80)
        f_main = ImageFont.load_default(size=300)
        f_side = ImageFont.load_default(size=100)
    except:
        f_train = f_route = f_main = f_side = ImageFont.load_default()

    # Малюємо плашку номера поїзда
    draw.rounded_rectangle([380, 20, 620, 110], radius=15, fill="black")
    draw.text((500, 65), train_no, fill="white", anchor="mm", font=f_train)

    # Маршрут
    draw.text((500, 180), route_ua, fill="black", anchor="mm", font=f_route)
    draw.text((500, 270), route_en, fill="black", anchor="mm", font=f_route)

    # Номер вагона
    draw.text((500, 480), str(vagon), fill="black", anchor="mm", font=f_main)

    # Сусіди
    if left_v:
        draw.text((150, 550), str(left_v), fill="black", anchor="mm", font=f_side)
        draw.text((150, 630), "◀", fill="black", anchor="mm", font=f_side)
    if right_v:
        draw.text((850, 550), str(right_v), fill="black", anchor="mm", font=f_side)
        draw.text((850, 630), "▶", fill="black", anchor="mm", font=f_side)
    
    return img

if st.button("🚀 Згенерувати макети"):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for v in range(start_v, end_v + 1):
            prev = v - 1 if v > start_v else None
            nxt = v + 1 if v < end_v else None
            
            # Варіант 1: Прямий
            img1 = create_image(v, prev, nxt)
            buf1 = io.BytesIO(); img1.save(buf1, format="PNG")
            zip_file.writestr(f"vagon_{v}_direct.png", buf1.getvalue())
            
            # Варіант 2: Зворотний (дзеркальний)
            img2 = create_image(v, nxt, prev)
            buf2 = io.BytesIO(); img2.save(buf2, format="PNG")
            zip_file.writestr(f"vagon_{v}_reverse.png", buf2.getvalue())
            
    st.download_button("📥 Скачати ZIP з усіма макетами", zip_buffer.getvalue(), "boards.zip")
