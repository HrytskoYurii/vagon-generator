import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

# Налаштування сторінки
st.set_page_config(page_title="Маршрутна табличка", layout="centered")
st.title("🚉 Генератор: Маршрутна табличка")

# Константи для друку (300 DPI)
DPI = 300
MM_TO_PX = DPI / 25.4

# РОЗМІРИ А4 (Книжкова орієнтація)
WIDTH = int(210 * MM_TO_PX)
HEIGHT = int(297 * MM_TO_PX)

def mm(value): return int(value * MM_TO_PX)
def pt(value): return int(value * (DPI / 72))

with st.sidebar:
    st.header("⚙️ Дані")
    train_no = st.text_input("Номер поїзда", value="19/20")
    route_ua = st.text_input("Назва (UA)", value="КИЇВ — ХЕЛМ")
    route_en = st.text_input("Назва (EN)", value="KYIV — CHELM")
    
    st.divider()
    st.header("🔢 Вагони")
    col1, col2 = st.columns(2)
    start_v = col1.number_input("З вагона", min_value=1, value=14)
    end_v = col2.number_input("По вагон", min_value=1, value=16)

def draw_arrow_below(draw, num_bbox, direction="left"):
    # Розрахунок центру стрілки під цифрою
    num_center_x = (num_bbox[0] + num_bbox[2]) / 2
    arrow_y_top = num_bbox[3] + mm(5) # 5мм відступ вниз від цифри
    
    w, h = mm(12), mm(10)
    
    if direction == "left":
        # Вершини трикутника (носик вліво)
        points = [
            (num_center_x + w/2, arrow_y_top),           # верхній правий
            (num_center_x + w/2, arrow_y_top + h),       # нижній правий
            (num_center_x - w/2, arrow_y_top + h/2)      # носик (ліво)
        ]
    else:
        # Вершини трикутника (носик вправо)
        points = [
            (num_center_x - w/2, arrow_y_top),           # верхній лівий
            (num_center_x - w/2, arrow_y_top + h),       # нижній лівий
            (num_center_x + w/2, arrow_y_top + h/2)      # носик (право)
        ]
    draw.polygon(points, fill="black")

def create_page(v_main, v_left, v_right):
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    font_file = "inter-bold.ttf"
    
    try:
        f_28 = ImageFont.truetype(font_file, pt(28))
        f_52 = ImageFont.truetype(font_file, pt(52))
        f_190 = ImageFont.truetype(font_file, pt(190))
    except:
        st.error(f"Файл {font_file} не знайдено!")
        return None

    # --- 1. Верхній блок ---
    bw, bh = mm(60), mm(30)
    bx, by = (WIDTH - bw) // 2, mm(15)
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=mm(8), fill="black")
    draw.text((WIDTH/2, by + bh/2), train_no, fill="white", font=f_28, anchor="mm")

    # --- 2. Назви маршрутів ---
    ua_y = by + bh + mm(12)
    draw.text((WIDTH/2, ua_y), route_ua, fill="black", font=f_52, anchor="mt")
    
    ua_bbox = draw.textbbox((WIDTH/2, ua_y), route_ua, font=f_52, anchor="mt")
    en_y = ua_bbox[3] + mm(5)
    draw.text((WIDTH/2, en_y), route_en, fill="black", font=f_28, anchor="mt")

    # --- 3. Центральне число ---
    en_bbox = draw.textbbox((WIDTH/2, en_y), route_en, font=f_28, anchor="mt")
    main_y = en_bbox[3] + mm(20)
    draw.text((WIDTH/2, main_y), str(v_main), fill="black", font=f_190, anchor="mt")

    # Розрахунок вертикального центру для бічних цифр
    main_bbox = draw.textbbox((WIDTH/2, main_y), str(v_main), font=f_190, anchor="mt")
    cy_sides = (main_bbox[1] + main_bbox[3]) / 2

    # --- 4. Бічні числа та стрілки ЗНИЗУ ---
    # Ліва сторона
    if v_left:
        lx = mm(15 + 5)
        draw.text((lx, cy_sides), str(v_left), fill="black", font=f_52, anchor="lm")
        l_bbox = draw.textbbox((lx, cy_sides), str(v_left), font=f_52, anchor="lm")
        draw_arrow_below(draw, l_bbox, "left")

    # Права сторона
    if v_right:
        rx = WIDTH - mm(15 + 5)
        draw.text((rx, cy_sides), str(v_right), fill="black", font=f_52, anchor="rm")
        r_bbox = draw.textbbox((rx, cy_sides), str(v_right), font=f_52, anchor="rm")
        draw_arrow_below(draw, r_bbox, "right")

    return img

if st.button("🚀 Згенерувати макети"):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for v in range(int(start_v), int(end_v) + 1):
            p, n = (v-1 if v > start_v else None), (v+1 if v < end_v else None)
            
            # Сторона А
            img_a = create_page(v, p, n)
            if img_a:
                b = io.BytesIO(); img_a.save(b, format="PNG"); zip_file.writestr(f"vagon_{v}_A.png", b.getvalue())
            
            # Сторона Б
            img_b = create_page(v, n, p)
            if img_b:
                b = io.BytesIO(); img_b.save(b, format="PNG"); zip_file.writestr(f"vagon_{v}_B.png", b.getvalue())
            
            if v == start_v:
                st.image(img_a, caption=f"Попередній перегляд (Стрілки знизу)")

    st.download_button("📥 Скачати ZIP", zip_buf.getvalue(), "labels_A4_fixed.zip")
