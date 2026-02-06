import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

# Налаштування сторінки
st.set_page_config(page_title="Маршрутна табличка", layout="wide")
st.title("📋 Маршрутна табличка")

# Константи для друку (300 DPI)
DPI = 300
MM_TO_PX = DPI / 25.4

# РОЗМІРИ А4 (Альбомна)
WIDTH = int(297 * MM_TO_PX)
HEIGHT = int(210 * MM_TO_PX)
MAX_TEXT_WIDTH = WIDTH - mm(30)  # Максимальна ширина тексту (поля по 15мм)

def mm(value): return int(value * MM_TO_PX)
def pt(value): return int(value * (DPI / 72))

def get_dynamic_font(draw, text, font_path, max_pt, max_px_width):
    """Підбирає максимальний розмір шрифту, що вписується в ширину"""
    current_pt = max_pt
    font = ImageFont.truetype(font_path, pt(current_pt))
    
    # Зменшуємо шрифт, поки ширина тексту більша за дозволену
    while draw.textbbox((0, 0), text, font=font)[2] > max_px_width and current_pt > 20:
        current_pt -= 2
        font = ImageFont.truetype(font_path, pt(current_pt))
    return font

with st.sidebar:
    st.header("⚙️ Налаштування")
    train_no = st.text_input("№ Поїзда", value="19/20")
    route_ua = st.text_input("Напрямок (UA)", value="КИЇВ — ХЕЛМ")
    route_en = st.text_input("Напрямок (EN)", value="KYIV — CHELM")
    
    st.divider()
    st.header("🔢 Вагони")
    col1, col2 = st.columns(2)
    start_v = col1.number_input("З вагона", min_value=1, value=14)
    end_v = col2.number_input("По вагон", min_value=1, value=16)

def draw_arrow_below(draw, num_bbox, direction="left"):
    num_center_x = (num_bbox[0] + num_bbox[2]) / 2
    arrow_y_top = num_bbox[3] + mm(5) 
    w, h = mm(15), mm(12) 
    
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
        # ДИНАМІЧНИЙ ШРИФТ ДЛЯ UA
        f_ua = get_dynamic_font(draw, route_ua, font_file, 80, MAX_TEXT_WIDTH)
        # ДИНАМІЧНИЙ ШРИФТ ДЛЯ EN (щоб теж не вилазив)
        f_en = get_dynamic_font(draw, route_en, font_file, 60, MAX_TEXT_WIDTH)
        
        f_main_no = ImageFont.truetype(font_file, pt(300))
        f_side_no = ImageFont.truetype(font_file, pt(90))
    except:
        st.error(f"Файл {font_file} не знайдено!")
        return None

    # 1. Верхній блок (Номер поїзда)
    bw, bh = mm(95), mm(35)
    bx, by = (WIDTH - bw) // 2, mm(12)
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=mm(8), fill="black")
    draw.text((WIDTH/2, by + bh/2), train_no, fill="white", font=f_train, anchor="mm")

    # 2. Назви маршрутів (UA)
    ua_y = by + bh + mm(10)
    draw.text((WIDTH/2, ua_y), route_ua, fill="black", font=f_ua, anchor="mt")
    
    # Визначаємо координату Y для EN на основі реальної висоти UA
    ua_bbox = draw.textbbox((WIDTH/2, ua_y), route_ua, font=f_ua, anchor="mt")
    en_y = ua_bbox[3] + mm(3)
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

if st.button("🚀 Згенерувати таблички"):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for v in range(int(start_v), int(end_v) + 1):
            p, n = (v-1 if v > start_v else None), (v+1 if v < end_v else None)
            img_a = create_landscape_page(v, p, n)
            if img_a:
                b = io.BytesIO(); img_a.save(b, format="PNG"); zip_file.writestr(f"vagon_{v}_A.png", b.getvalue())
            img_b = create_landscape_page(v, n, p)
            if img_b:
                b = io.BytesIO(); img_b.save(b, format="PNG"); zip_file.writestr(f"vagon_{v}_B.png", b.getvalue())
            if v == start_v:
                st.image(img_a, caption="Попередній перегляд (Шрифт адаптується)")

    st.download_button("📥 Завантажити ZIP", zip_buf.getvalue(), "labels_auto_font.zip")
