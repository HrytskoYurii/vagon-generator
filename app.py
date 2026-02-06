import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

st.set_page_config(page_title="Vagon Gen Heavy", layout="centered")

st.title("🚉 Генератор дощок (Bold Version)")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Налаштування")
    train_no = st.text_input("№ Поїзда", value="19/20")
    route_ua = st.text_input("Напрямок (UA)", value="КИЇВ — ХЕЛМ")
    route_en = st.text_input("Напрямок (EN)", value="KYIV — CHELM")
    
    col_v1, col_v2 = st.columns(2)
    start_v = col_v1.number_input("З вагона", min_value=1, value=14)
    end_v = col_v2.number_input("По вагон", min_value=1, value=16)

# --- Функція для малювання ЖИРНОГО тексту з інтервалами ---
def draw_bold_text(draw, text, position, font, fill="black", spacing=0, thickness=2):
    # thickness=2 робить текст товстішим, малюючи його кілька разів зі зміщенням
    sum_width = sum(draw.textbbox((0, 0), char, font=font)[2] for char in text)
    total_width = sum_width + spacing * (len(text) - 1)
    
    x, y = position
    current_x = x - total_width / 2

    for char in text:
        # Малюємо символ кілька разів для екстремальної жирності
        for off_x in range(-thickness, thickness + 1):
            for off_y in range(-thickness, thickness + 1):
                draw.text((current_x + off_x, y + off_y), char, font=font, fill=fill, anchor="lm")
        
        char_width = draw.textbbox((0, 0), char, font=font)[2]
        current_x += char_width + spacing

def create_board(vagon, left_v, right_v):
    width, height = 2400, 1600 
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    font_path = "SourceSans3-VariableFont_wght.ttf"

    try:
        # Завантажуємо шрифт
        f_train = ImageFont.truetype(font_path, 150)
        f_route = ImageFont.truetype(font_path, 130)
        f_vagon = ImageFont.truetype(font_path, 610)
        f_side = ImageFont.truetype(font_path, 200)
        f_arrow = ImageFont.truetype(font_path, 150)
    except:
        st.error("Шрифт не знайдено на GitHub!")
        return None

    # 1. Номер поїзда (Чорна плашка + жирний текст)
    box_w = 750
    draw.rounded_rectangle([width/2-box_w/2, 50, width/2+box_w/2, 250], radius=40, fill="black")
    draw_bold_text(draw, train_no, (width/2, 150), f_train, fill="white", spacing=30, thickness=2)

    # 2. Напрямок UA/EN (Жирний, інтервал 0)
    draw_bold_text(draw, route_ua, (width/2, 420), f_route, spacing=0, thickness=2)
    draw_bold_text(draw, route_en, (width/2, 570), f_route, spacing=0, thickness=2)

    # 3. Номер вагона (ЕКСТРЕМАЛЬНО жирний)
    draw_bold_text(draw, str(vagon), (width/2, height/2 + 180), f_vagon, spacing=30, thickness=4)

    # 4. Сусідні вагони
    if left_v:
        draw_bold_text(draw, str(left_v), (350, 1350), f_side, spacing=30, thickness=2)
        draw.text((350, 1500), "◀", fill="black", anchor="mm", font=f_arrow)
    if right_v:
        draw_bold_text(draw, str(right_v), (width - 350, 1350), f_side, spacing=30, thickness=2)
        draw.text((width - 350, 1500), "▶", fill="black", anchor="mm", font=f_arrow)
    
    return img

# --- Кнопка виконання ---
if st.button("🚀 Згенерувати жирні макети"):
    if not start_v or not end_v:
        st.warning("Вкажіть номери вагонів")
    else:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
            for v in range(int(start_v), int(end_v) + 1):
                p, n = (v-1 if v > start_v else None), (v+1 if v < end_v else None)
                
                # Сторона 1
                img1 = create_board(v, p, n)
                if img1:
                    buf1 = io.BytesIO(); img1.save(buf1, format="PNG")
                    zip_file.writestr(f"vagon_{v:02d}_side1.png", buf1.getvalue())
                
                # Сторона 2
                img2 = create_board(v, n, p)
                if img2:
                    buf2 = io.BytesIO(); img2.save(buf2, format="PNG")
                    zip_file.writestr(f"vagon_{v:02d}_side2.png", buf2.getvalue())
                
                if v == start_v:
                    st.image(img1, caption="Попередній перегляд (Жирний шрифт)")

        st.download_button("📥 Завантажити ZIP", zip_buffer.getvalue(), "boards_bold.zip")
