import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

def create_overview(dark_mode=False, output_path="overview.png"):
    dataset_dir = Path(r"C:\Users\phu14\Downloads\archive\dataset")
    
    classes_info = [
        {"id": "banh_bo", "name": "Bánh Bò", "en": "Steamed Rice Cake", "img": "banh_bo154.jpg", "count": 300},
        {"id": "banh_bot_loc", "name": "Bánh Bột Lọc", "en": "Clear Tapioca Dumpling", "img": "banh_bot_loc117.jpg", "count": 300},
        {"id": "banh_cong", "name": "Bánh Cống", "en": "Soc Trang Fried Cake", "img": "banh_cong153.jpg", "count": 232},
        {"id": "banh_da_lon", "name": "Bánh Da Lợn", "en": "Steamed Layer Cake", "img": "banh_da_lon144.jpg", "count": 300},
        {"id": "banh_khot", "name": "Bánh Khọt", "en": "Mini Savory Pancakes", "img": "banh_khot145.jpg", "count": 300},
        {"id": "banh_mi", "name": "Bánh Mì", "en": "Vietnamese Baguette", "img": "BanhMi142.jpg", "count": 300},
        {"id": "banh_tai_heo", "name": "Bánh Tai Heo", "en": "Pig Ear Biscuits", "img": "banh_tai_heo123.jpg", "count": 300},
        {"id": "banh_tieu", "name": "Bánh Tiêu", "en": "Hollow Sesame Donut", "img": "banh_tieu104.jpg", "count": 286},
        {"id": "banh_trung_thu", "name": "Bánh Trung Thu", "en": "Mooncake", "img": "banh_trung_thu110.jpg", "count": 247},
        {"id": "banh_xeo", "name": "Bánh Xèo", "en": "Crispy Sizzling Crepe", "img": "banh_xeo130.jpg", "count": 300},
    ]

    # Canvas dimensions: 2 rows x 5 columns
    cols = 5
    rows = 2
    
    card_w = 420
    card_h = 500
    img_size = 380  # inner photo square
    
    pad_x = 35
    pad_y = 35
    margin_top = 220
    margin_bottom = 120
    margin_left = 60
    margin_right = 60
    
    width = margin_left + cols * card_w + (cols - 1) * pad_x + margin_right
    height = margin_top + rows * card_h + (rows - 1) * pad_y + margin_bottom
    
    # Palette
    if dark_mode:
        bg_color = (15, 23, 42)          # Slate 900
        card_bg = (30, 41, 59)           # Slate 800
        card_border = (51, 65, 85)       # Slate 700
        text_primary = (248, 250, 252)   # Slate 50
        text_secondary = (148, 163, 184) # Slate 400
        badge_bg = (234, 88, 12)         # Primary Orange
        badge_text = (255, 255, 255)
        tag_bg = (15, 23, 42)
        tag_text = (56, 189, 248)        # Sky 400
        header_color = (255, 255, 255)
        sub_color = (148, 163, 184)
    else:
        bg_color = (248, 250, 252)       # Slate 50
        card_bg = (255, 255, 255)        # Pure White
        card_border = (226, 232, 240)    # Slate 200
        text_primary = (15, 23, 42)      # Slate 900
        text_secondary = (100, 116, 139) # Slate 500
        badge_bg = (234, 88, 12)         # Orange 600
        badge_text = (255, 255, 255)
        tag_bg = (241, 245, 249)         # Slate 100
        tag_text = (2, 132, 199)         # Sky 600
        header_color = (15, 23, 42)
        sub_color = (71, 85, 105)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Fonts
    font_path = "C:/Windows/Fonts/segoeui.ttf"
    font_bold_path = "C:/Windows/Fonts/segoeuib.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
        font_path = "C:/Windows/Fonts/arial.ttf"

    font_title = ImageFont.truetype(font_bold_path, 54)
    font_subtitle = ImageFont.truetype(font_path, 26)
    font_card_title = ImageFont.truetype(font_bold_path, 28)
    font_card_sub = ImageFont.truetype(font_path, 20)
    font_badge = ImageFont.truetype(font_bold_path, 18)
    font_tag = ImageFont.truetype(font_bold_path, 17)
    font_footer = ImageFont.truetype(font_path, 22)

    # 1. Header Banner
    title_text = "HÌNH TỔNG QUAN 10 LỚP MÓN ĂN ĐƯỢC HỆ THỐNG NHẬN DIỆN"
    # Measure text
    bbox = draw.textbbox((0, 0), title_text, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, 50), title_text, fill=header_color, font=font_title)

    sub_text = "Tập dữ liệu nhận diện món ăn truyền thống Việt Nam (10 Vietnamese Traditional Food Classes Dataset)"
    sbbox = draw.textbbox((0, 0), sub_text, font=font_subtitle)
    stw = sbbox[2] - sbbox[0]
    draw.text(((width - stw) // 2, 125), sub_text, fill=sub_color, font=font_subtitle)

    # Accent decorative line under header
    line_w = 600
    line_x = (width - line_w) // 2
    draw.line([(line_x, 175), (line_x + line_w, 175)], fill=(234, 88, 12), width=4)

    # 2. Render Cards
    for idx, item in enumerate(classes_info):
        r = idx // cols
        c = idx % cols
        
        x0 = margin_left + c * (card_w + pad_x)
        y0 = margin_top + r * (card_h + pad_y)
        x1 = x0 + card_w
        y1 = y0 + card_h

        # Card container with rounded rectangle
        draw.rounded_rectangle([x0, y0, x1, y1], radius=20, fill=card_bg, outline=card_border, width=2)

        # Load and center-crop food image
        img_file = dataset_dir / item["id"] / item["img"]
        if not img_file.exists():
            # fallback to first image in directory
            img_file = next((dataset_dir / item["id"]).glob("*.*"))

        with Image.open(img_file) as f_img:
            f_img = f_img.convert("RGB")
            # Square center crop
            w, h = f_img.size
            min_dim = min(w, h)
            left = (w - min_dim) // 2
            top = (h - min_dim) // 2
            f_crop = f_img.crop((left, top, left + min_dim, top + min_dim))
            f_crop = f_crop.resize((img_size, img_size), Image.Resampling.LANCZOS)
            
            # Mask with rounded corners for photo
            mask = Image.new("L", (img_size, img_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([0, 0, img_size, img_size], radius=14, fill=255)
            
            # Paste photo onto canvas
            photo_x = x0 + (card_w - img_size) // 2
            photo_y = y0 + 20
            img.paste(f_crop, (photo_x, photo_y), mask)

        # Number Badge overlay on image (top left of photo)
        badge_w, badge_h = 95, 34
        bx0 = photo_x + 12
        by0 = photo_y + 12
        draw.rounded_rectangle([bx0, by0, bx0 + badge_w, by0 + badge_h], radius=10, fill=badge_bg)
        badge_lbl = f"Lớp #{idx+1:02d}"
        bb = draw.textbbox((0, 0), badge_lbl, font=font_badge)
        draw.text((bx0 + (badge_w - (bb[2] - bb[0])) // 2, by0 + 6), badge_lbl, fill=badge_text, font=font_badge)

        # Text below photo: Vietnamese Name
        text_y = photo_y + img_size + 16
        name_str = item["name"]
        nb = draw.textbbox((0, 0), name_str, font=font_card_title)
        draw.text((x0 + (card_w - (nb[2] - nb[0])) // 2, text_y), name_str, fill=text_primary, font=font_card_title)

        # Sub-info row: Code ID & Sample Count tag
        info_str = f"{item['id']}  •  {item['count']} ảnh"
        ib = draw.textbbox((0, 0), info_str, font=font_card_sub)
        draw.text((x0 + (card_w - (ib[2] - ib[0])) // 2, text_y + 36), info_str, fill=text_secondary, font=font_card_sub)

    # 3. Footer info
    footer_text = "Hệ thống Nhận diện Thị giác Máy tính AI  |  Tổng mẫu: 2,865 ảnh (10 lớp)  |  Phân bố: 70% Train - 15% Val - 15% Test  |  YOLOv8s & Custom CNN"
    fb = draw.textbbox((0, 0), footer_text, font=font_footer)
    fw = fb[2] - fb[0]
    draw.text(((width - fw) // 2, height - 70), footer_text, fill=text_secondary, font=font_footer)

    img.save(output_path, quality=95)
    print(f"Đã tạo thành công: {output_path} ({width}x{height}px)")

if __name__ == "__main__":
    create_overview(dark_mode=False, output_path=r"C:\XLA\static\img\overview_10_classes_white.png")
    create_overview(dark_mode=True, output_path=r"C:\XLA\static\img\overview_10_classes_dark.png")
