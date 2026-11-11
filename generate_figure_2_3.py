import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

def apply_augmentations(base_img):
    w, h = base_img.size
    
    # 1. Original
    orig = base_img.copy()

    # 2. Horizontal Flip
    flip = base_img.transpose(Image.FLIP_LEFT_RIGHT)

    # 3. Brighten (+40%)
    bright = ImageEnhance.Brightness(base_img).enhance(1.4)

    # 4. Darken (-45%)
    dark = ImageEnhance.Brightness(base_img).enhance(0.55)

    # 5. Contrast (+50%)
    contrast = ImageEnhance.Contrast(base_img).enhance(1.5)

    # 6. Saturation / Color Jitter (+70%)
    saturation = ImageEnhance.Color(base_img).enhance(1.7)

    # 7. Rotation (+18 degrees, center crop back to square)
    rotated = base_img.rotate(18, resample=Image.BICUBIC, expand=False)

    # 8. Random Zoom & Crop (scale 80% center)
    crop_w, crop_h = int(w * 0.8), int(h * 0.8)
    cx, cy = (w - crop_w) // 2, (h - crop_h) // 2
    zoom = base_img.crop((cx, cy, cx + crop_w, cy + crop_h)).resize((w, h), Image.Resampling.LANCZOS)

    # 9. Gaussian Blur (radius 3.5)
    blur = base_img.filter(ImageFilter.GaussianBlur(radius=3.5))

    # 10. Cutout / Random Erasing
    cutout = base_img.copy()
    draw_cut = ImageDraw.Draw(cutout)
    box_w, box_h = int(w * 0.35), int(h * 0.35)
    bx0, by0 = int(w * 0.32), int(h * 0.32)
    draw_cut.rounded_rectangle([bx0, by0, bx0 + box_w, by0 + box_h], radius=10, fill=(35, 35, 35))

    return [
        {"id": "orig", "title": "Ảnh Gốc (Original)", "tag": "Chuẩn 448x448", "sub": "Ảnh mẫu chưa biến đổi", "desc": "Kích thước chuẩn hóa đầu vào", "img": orig, "tag_color": (234, 88, 12)},
        {"id": "flip", "title": "Lật Ngang Đối Xứng", "tag": "Fliplr (p = 0.5)", "sub": "RandomHorizontalFlip", "desc": "Bất biến theo hướng nhìn đối xứng", "img": flip, "tag_color": (16, 185, 129)},
        {"id": "bright", "title": "Tăng Độ Sáng (+40%)", "tag": "Brightness (1.4x)", "sub": "ColorJitter(brightness=0.4)", "desc": "Mô phỏng nguồn sáng chói, ngoài trời", "img": bright, "tag_color": (234, 179, 8)},
        {"id": "dark", "title": "Giảm Độ Sáng (-45%)", "tag": "Brightness (0.55x)", "sub": "ColorJitter(brightness=0.45)", "desc": "Mô phỏng môi trường tối, thiếu sáng", "img": dark, "tag_color": (100, 116, 139)},
        {"id": "contrast", "title": "Tăng Tương Phản (+50%)", "tag": "Contrast (1.5x)", "sub": "ColorJitter(contrast=0.5)", "desc": "Tách biệt rõ các chi tiết viền và vân", "img": contrast, "tag_color": (168, 85, 247)},
        {"id": "saturation", "title": "Tăng Bão Hòa Màu (+70%)", "tag": "Saturation (1.7x)", "sub": "ColorJitter(saturation=0.7)", "desc": "Bất biến với sai lệch cảm biến camera", "img": saturation, "tag_color": (236, 72, 153)},
        {"id": "rotate", "title": "Xoay Góc Nghiêng (±20°)", "tag": "Rotation (±20°)", "sub": "RandomRotation(degrees=20)", "desc": "Bất biến khi chụp góc nghiêng, lệch", "img": rotated, "tag_color": (14, 165, 233)},
        {"id": "zoom", "title": "Thu Phóng & Cắt Tỉa", "tag": "Crop & Zoom (80%)", "sub": "RandomResizedCrop(scale=0.8)", "desc": "Mô phỏng chụp cận cảnh (close-up)", "img": zoom, "tag_color": (249, 115, 22)},
        {"id": "blur", "title": "Làm Mờ Ống Kính (Blur)", "tag": "Gaussian (r = 3.5)", "sub": "GaussianBlur(radius=3.5)", "desc": "Mô phỏng rung lắc tay hoặc out nét", "img": blur, "tag_color": (139, 92, 246)},
        {"id": "cutout", "title": "Che Khuất Cục Bộ (Cutout)", "tag": "Random Erasing", "sub": "Cutout / Occlusion Mask", "desc": "Nhận diện vật thể bị che một phần", "img": cutout, "tag_color": (239, 68, 68)},
    ]

def create_augmentation_figure(dark_mode=False, output_path="hinh_2_3.png"):
    width = 2400
    height = 1450

    if dark_mode:
        bg_color = (15, 23, 42)          # Slate 900
        card_bg = (30, 41, 59)           # Slate 800
        card_border = (51, 65, 85)       # Slate 700
        text_primary = (248, 250, 252)   # Slate 50
        text_secondary = (148, 163, 184) # Slate 400
        text_desc = (203, 213, 225)      # Slate 300
        header_color = (255, 255, 255)
    else:
        bg_color = (248, 250, 252)       # Slate 50
        card_bg = (255, 255, 255)        # Pure White
        card_border = (226, 232, 240)    # Slate 200
        text_primary = (15, 23, 42)      # Slate 900
        text_secondary = (100, 116, 139) # Slate 500
        text_desc = (71, 85, 105)        # Slate 600
        header_color = (15, 23, 42)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Fonts
    font_bold_path = "C:/Windows/Fonts/segoeuib.ttf"
    font_path = "C:/Windows/Fonts/segoeui.ttf"
    font_mono = "C:/Windows/Fonts/consola.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_mono = "C:/Windows/Fonts/cour.ttf"

    font_title = ImageFont.truetype(font_bold_path, 48)
    font_sub = ImageFont.truetype(font_path, 24)
    font_card_title = ImageFont.truetype(font_bold_path, 24)
    font_badge = ImageFont.truetype(font_bold_path, 17)
    font_card_sub = ImageFont.truetype(font_mono, 18)
    font_card_desc = ImageFont.truetype(font_path, 19)
    font_footer = ImageFont.truetype(font_path, 21)

    # Header
    title_text = "HÌNH 2.3: MINH HỌA CÁC KỸ THUẬT TĂNG CƯỜNG DỮ LIỆU"
    bbox = draw.textbbox((0, 0), title_text, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, 45), title_text, fill=header_color, font=font_title)

    sub_text = "Mô phỏng các phép biến đổi không gian và màu sắc trong pipeline huấn luyện mô hình YOLOv8s & Custom CNN"
    sbbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    stw = sbbox[2] - sbbox[0]
    draw.text(((width - stw) // 2, 115), sub_text, fill=text_secondary, font=font_sub)

    line_w = 700
    line_x = (width - line_w) // 2
    draw.line([(line_x, 160), (line_x + line_w, 160)], fill=(234, 88, 12), width=4)

    # Prepare base image: load BanhMi142.jpg or banh_xeo130.jpg center square
    sample_path = r"C:\Users\phu14\Downloads\archive\dataset\banh_mi\BanhMi142.jpg"
    if not os.path.exists(sample_path):
        sample_path = r"C:\Users\phu14\Downloads\archive\dataset\banh_xeo\banh_xeo130.jpg"

    with Image.open(sample_path) as raw_img:
        raw_img = raw_img.convert("RGB")
        w, h = raw_img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        sq_img = raw_img.crop((left, top, left + min_dim, top + min_dim))
        sq_img = sq_img.resize((400, 400), Image.Resampling.LANCZOS)

    aug_list = apply_augmentations(sq_img)

    # Grid 2 rows x 5 cols
    cols = 5
    rows = 2
    card_w = 425
    card_h = 540
    img_inner = 385
    pad_x = 35
    pad_y = 35
    margin_top = 190
    margin_left = (width - (cols * card_w + (cols - 1) * pad_x)) // 2

    for idx, item in enumerate(aug_list):
        r = idx // cols
        c = idx % cols
        x0 = margin_left + c * (card_w + pad_x)
        y0 = margin_top + r * (card_h + pad_y)
        x1 = x0 + card_w
        y1 = y0 + card_h

        # Card box
        draw.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=card_bg, outline=card_border, width=2)

        # Transformed photo with rounded corners
        t_img = item["img"].resize((img_inner, img_inner), Image.Resampling.LANCZOS)
        mask = Image.new("L", (img_inner, img_inner), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, img_inner, img_inner], radius=12, fill=255)
        
        px = x0 + (card_w - img_inner) // 2
        py = y0 + 18
        img.paste(t_img, (px, py), mask)

        # Badge tag overlay on image (top right)
        tag_text = item["tag"]
        tb = draw.textbbox((0, 0), tag_text, font=font_badge)
        tag_w = tb[2] - tb[0] + 24
        tag_h = 32
        tx1 = px + img_inner - 12
        tx0 = tx1 - tag_w
        ty0 = py + 12
        draw.rounded_rectangle([tx0, ty0, tx1, ty0 + tag_h], radius=8, fill=item["tag_color"])
        draw.text((tx0 + 12, ty0 + 6), tag_text, fill=(255, 255, 255), font=font_badge)

        # Step index badge (top left)
        idx_text = f"#{idx+1:02d}"
        ib = draw.textbbox((0, 0), idx_text, font=font_badge)
        iw = ib[2] - ib[0] + 20
        draw.rounded_rectangle([px + 12, ty0, px + 12 + iw, ty0 + tag_h], radius=8, fill=(15, 23, 42))
        draw.text((px + 22, ty0 + 6), idx_text, fill=(248, 250, 252), font=font_badge)

        # Text labels below image
        text_y = py + img_inner + 14
        # Title
        draw.text((x0 + 20, text_y), item["title"], fill=text_primary, font=font_card_title)
        # Function sub
        draw.text((x0 + 20, text_y + 32), item["sub"], fill=item["tag_color"], font=font_card_sub)
        # Explanation desc
        draw.text((x0 + 20, text_y + 60), item["desc"], fill=text_desc, font=font_card_desc)

    # Footer
    foot_text = "Hình 2.3: Minh họa các kỹ thuật tăng cường dữ liệu (Data Augmentation)  |  Mục tiêu: Chống Overfitting & Tăng tính khái quát hóa cho mô hình AI"
    fb = draw.textbbox((0, 0), foot_text, font=font_footer)
    fw = fb[2] - fb[0]
    draw.text(((width - fw) // 2, height - 60), foot_text, fill=text_secondary, font=font_footer)

    img.save(output_path, quality=95)
    print(f"Đã tạo thành công: {output_path} ({width}x{height}px)")

if __name__ == "__main__":
    create_augmentation_figure(dark_mode=False, output_path=r"C:\XLA\static\img\hinh_2_3_data_augmentation_white.png")
    create_augmentation_figure(dark_mode=True, output_path=r"C:\XLA\static\img\hinh_2_3_data_augmentation_dark.png")
