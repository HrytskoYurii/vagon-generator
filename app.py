import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

# Налаштування сторінки
st.set_page_config(page_title="Маршрутна табличка PRO", layout="wide")
st.title("🚉 Генератор: Альбомна табличка (90/300/90)")

# Константи для друку (300 DPI)
DPI = 300
MM_TO_PX = DPI / 25.4

# РОЗМІРИ А4 (Альбомна)
WIDTH = int(297 * MM_TO_PX)
HEIGHT = int(210 * MM_TO_PX)

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
    # Центрування по горизонталі відносно великої цифри 90pt
    num_center_x = (num_bbox[0] + num_bbox[2]) / 2
    arrow_y_top = num_bbox[3] + mm(5) 
    
    w, h = mm(15), mm(12) # Трохи збільшив стрілки під шрифт 90
    
    if direction == "left":
        points = [(num_center_x + w/2, arrow_y_top), (num_center_x + w/2, arrow_y_top + h), (num_center_x - w/2, arrow_y_top + h/2)]
    else:
        points = [(num_center_x - w/2, arrow_y_top), (num_center_x - w/2, arrow_y_top + h), (num_center_x + w/2, arrow_y_top + h/2)]
    draw.polygon(points, fill="black")

def create_landscape_page(v_main, v_left, v_right):
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    font_file = "inter-bold.ttf"
    
    try:
        f_train = ImageFont.truetype(font_file, pt(60))
        f_ua = ImageFont.truetype(font_file, pt(80))
        f_en = ImageFont.truetype(font_file, pt(60))
        f_main_no = ImageFont.truetype(font_file, pt(300))
        f_side_no = ImageFont.truetype(font_file, pt(90)) # ВСТАНОВЛЕНО 90
    except:
        st.error(f"Файл {font_file} не знайдено!")
        return None

    # 1. Верхній блок (Номер поїзда)
    bw, bh = mm(90), mm(35)
    bx, by = (WIDTH - bw) // 2, mm(10)
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=mm(8), fill="black")
    draw.text((WIDTH/2, by + bh/2), train_no, fill="white", font=f_train, anchor="mm")

    # 2. Назви маршрутів
    ua_y = by + bh + mm(8)
    draw.text((WIDTH/2, ua_y), route_ua, fill="black", font=f_ua, anchor="mt")
    
    ua_bbox = draw.textbbox((WIDTH/2, ua_y), route_ua, font=f_ua, anchor="mt")
    en_y = ua_bbox[3] + mm(2)
    draw.text((WIDTH/2, en_y), route_en, fill="black", font=f_en, anchor="mt")

    # 3. Центральне число (300 pt)
    en_bbox = draw.textbbox((WIDTH/2, en_y), route_en, font=f_en, anchor="mt")
    main_y = en_bbox[3] + mm(5)
    draw.text((WIDTH/2, main_y), str(v_main), fill="black", font=f_main_no, anchor="mt")

    # Центр для бокових цифр
    main_bbox = draw.textbbox((WIDTH/2, main_y), str(v_main), font=f_main_no, anchor="mt")
    cy_sides = (main_bbox[1] + main_bbox[3]) / 2

    # 4. Бічні числа (90 pt) та стрілки
    side_margin = mm(25) 
    if v_left:
        lx = side_margin
        draw.text((lx, cy_sides), str(v_left), fill="black", font=f_side_no, anchor="lm")
        l_bbox = draw.textbbox((lx, cy_sides), str(v_left), font=f_side_no, anchor="lm")
        draw_arrow_below(draw, l_bbox, "left")

    if v_right:
        rx = WIDTH - side_margin
        draw.text((rx, cy_sides), str(v_right), fill="black", font=f_side_no, anchor="rm")
        r_bbox = draw.textbbox((rx, cy_sides), str(v_right), font=f_side_no, anchor="rm")
        draw_arrow_below(draw, r_bbox, "right")

    return img

if st.button("🚀 Згенерувати фінальні макети"):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for v in range(int(start_v), int(end_v) + 1):
            p, n = (v-1 if v > start_v else None), (v+1 if v < end_v else None)
            
            img_a = create_landscape_page(v, p, n)
            if img_a:
                b = io.BytesIO(); img_a.save(b, format="PNG"); zip_file.writestr(f"vagon_{v}_sideA.png", b.getvalue())
            
            img_b = create_landscape_page(v, n, p)
            if img_b:
                b = io.BytesIO(); img_b.save(b, format="PNG"); zip_file.writestr(f"vagon_{v}_sideB.png", b.getvalue())
            
            if v == start_v:
                st.image(img_a, caption="Попередній перегляд (Сусідні вагони 90 pt)")

    st.download_button("📥 Завантажити ZIP", zip_buf.getvalue(), "labels_final_90pt.zip")
