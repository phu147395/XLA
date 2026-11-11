import os
from PIL import Image, ImageDraw, ImageFont

def draw_folder_icon(draw, x, y, size=24, color=(245, 158, 11)):
    # Draw a cute folder icon
    w, h = size, int(size * 0.75)
    tab_w, tab_h = int(w * 0.4), int(h * 0.3)
    # folder tab
    draw.rounded_rectangle([x, y, x + tab_w, y + tab_h + 3], radius=2, fill=color)
    # folder body
    draw.rounded_rectangle([x, y + tab_h, x + w, y + h + tab_h], radius=3, fill=color)

def draw_file_icon(draw, x, y, size=22, color=(59, 130, 246)):
    # Draw a cute document/image file icon
    w, h = int(size * 0.8), size
    draw.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=color)
    # folded corner
    draw.polygon([(x + w - 6, y), (x + w, y + 6), (x + w - 6, y + 6)], fill=(255, 255, 255))

def create_directory_structure_figure(dark_mode=False, output_path="hinh_2_2.png"):
    width = 2400
    height = 1450

    if dark_mode:
        bg_color = (15, 23, 42)          # Slate 900
        card_bg = (30, 41, 59)           # Slate 800
        card_border = (51, 65, 85)       # Slate 700
        inner_bg = (15, 23, 42)          # Slate 900
        text_primary = (248, 250, 252)   # Slate 50
        text_secondary = (148, 163, 184) # Slate 400
        text_accent = (56, 189, 248)     # Sky 400
        tree_line_color = (100, 116, 139)# Slate 500
        badge_train = (16, 185, 129)     # Emerald 500
        badge_val = (59, 130, 246)       # Blue 500
        badge_test = (168, 85, 247)      # Purple 500
        header_color = (255, 255, 255)
        folder_color = (245, 158, 11)    # Amber 500
        folder_root = (234, 88, 12)      # Orange 600
    else:
        bg_color = (248, 250, 252)       # Slate 50
        card_bg = (255, 255, 255)        # White
        card_border = (226, 232, 240)    # Slate 200
        inner_bg = (241, 245, 249)       # Slate 100
        text_primary = (15, 23, 42)      # Slate 900
        text_secondary = (100, 116, 139) # Slate 500
        text_accent = (2, 132, 199)      # Sky 600
        tree_line_color = (148, 163, 184)# Slate 400
        badge_train = (5, 150, 105)      # Emerald 600
        badge_val = (37, 99, 235)        # Blue 600
        badge_test = (147, 51, 234)      # Purple 600
        header_color = (15, 23, 42)
        folder_color = (217, 119, 6)     # Amber 600
        folder_root = (234, 88, 12)      # Orange 600

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
    font_box_title = ImageFont.truetype(font_bold_path, 26)
    font_badge = ImageFont.truetype(font_bold_path, 18)
    font_tree_root = ImageFont.truetype(font_bold_path, 26)
    font_tree_branch = ImageFont.truetype(font_bold_path, 22)
    font_tree_leaf = ImageFont.truetype(font_mono, 20)
    font_tree_desc = ImageFont.truetype(font_path, 18)
    font_footer = ImageFont.truetype(font_path, 21)

    # 1. Header
    title_text = "HÌNH 2.2: CẤU TRÚC THƯ MỤC DỮ LIỆU"
    bbox = draw.textbbox((0, 0), title_text, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, 45), title_text, fill=header_color, font=font_title)

    sub_text = "Sơ đồ tổ chức cây thư mục bộ dữ liệu nhận diện 10 món ăn Việt Nam (Tỷ lệ phân chia 70% Train - 15% Val - 15% Test)"
    sbbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    stw = sbbox[2] - sbbox[0]
    draw.text(((width - stw) // 2, 115), sub_text, fill=text_secondary, font=font_sub)

    # Header accent line
    line_w = 650
    line_x = (width - line_w) // 2
    draw.line([(line_x, 160), (line_x + line_w, 160)], fill=(234, 88, 12), width=4)

    # 2. Main Content Layout: Left Card (Raw Source & Split Summary) + Right Card (Tree Hierarchy)
    top_y = 190
    content_h = 1140

    # Left Card: Quy trình phân chia dữ liệu (Width: 680px)
    left_x = 70
    left_w = 680
    draw.rounded_rectangle([left_x, top_y, left_x + left_w, top_y + content_h], radius=20, fill=card_bg, outline=card_border, width=2)

    # Left Card Header
    l_head = "1. TẬP DỮ LIỆU NGUỒN (RAW DATASET)"
    draw.text((left_x + 35, top_y + 35), l_head, fill=folder_root, font=font_box_title)

    # Raw Source Box
    raw_box_y = top_y + 85
    draw.rounded_rectangle([left_x + 30, raw_box_y, left_x + left_w - 30, raw_box_y + 240], radius=14, fill=inner_bg, outline=card_border, width=1)
    
    draw_folder_icon(draw, left_x + 55, raw_box_y + 22, size=32, color=folder_root)
    draw.text((left_x + 100, raw_box_y + 20), "archive/dataset/", fill=text_primary, font=font_tree_root)
    draw.text((left_x + 100, raw_box_y + 55), "Tổng cộng: 2.865 ảnh gốc (10 lớp)", fill=text_secondary, font=font_tree_desc)

    raw_items = [
        "├── banh_bo/ (300 ảnh)",
        "├── banh_bot_loc/ (300 ảnh)",
        "├── banh_cong/ (232 ảnh)",
        "├── ... (7 lớp món ăn khác)",
        "└── banh_xeo/ (300 ảnh)"
    ]
    for idx, r_item in enumerate(raw_items):
        draw.text((left_x + 70, raw_box_y + 90 + idx * 28), r_item, fill=text_secondary, font=font_tree_leaf)

    # Down Arrow: Pipeline Tiền Xử Lý
    arrow_y = raw_box_y + 265
    draw.line([(left_x + left_w // 2, arrow_y), (left_x + left_w // 2, arrow_y + 55)], fill=(234, 88, 12), width=3)
    draw.polygon([
        (left_x + left_w // 2 - 10, arrow_y + 50),
        (left_x + left_w // 2 + 10, arrow_y + 50),
        (left_x + left_w // 2, arrow_y + 68)
    ], fill=(234, 88, 12))

    proc_lbl = "Tiền xử lý & Chia dữ liệu (70 / 15 / 15)"
    pb = draw.textbbox((0, 0), proc_lbl, font=font_badge)
    draw.rounded_rectangle([left_x + (left_w - (pb[2] - pb[0]) - 30) // 2, arrow_y + 12, left_x + (left_w + (pb[2] - pb[0]) + 30) // 2, arrow_y + 44], radius=16, fill=(234, 88, 12))
    draw.text((left_x + (left_w - (pb[2] - pb[0])) // 2, arrow_y + 18), proc_lbl, fill=(255, 255, 255), font=font_badge)

    # Summary Stats Box
    stat_box_y = arrow_y + 90
    draw.rounded_rectangle([left_x + 30, stat_box_y, left_x + left_w - 30, top_y + content_h - 35], radius=14, fill=inner_bg, outline=card_border, width=1)

    draw.text((left_x + 55, stat_box_y + 25), "THỐNG KÊ PHÂN BỔ TẬP DỮ LIỆU", fill=text_primary, font=font_box_title)

    split_cards = [
        {"name": "TẬP TRAIN (HUẤN LUYỆN)", "pct": "70%", "count": "2.004 ảnh", "color": badge_train, "desc": "Cập nhật trọng số mô hình YOLO & CNN"},
        {"name": "TẬP VAL (KIỂM ĐỊNH)", "pct": "15%", "count": "428 ảnh", "color": badge_val, "desc": "Tối ưu siêu tham số & tránh Overfitting"},
        {"name": "TẬP TEST (KIỂM THỬ)", "pct": "15%", "count": "433 ảnh", "color": badge_test, "desc": "Đánh giá độc lập ma trận nhầm lẫn"}
    ]

    card_y = stat_box_y + 75
    for sc in split_cards:
        draw.rounded_rectangle([left_x + 50, card_y, left_x + left_w - 50, card_y + 105], radius=12, fill=card_bg, outline=card_border, width=1)
        # Color bar on the left
        draw.rounded_rectangle([left_x + 50, card_y, left_x + 58, card_y + 105], radius=4, fill=sc["color"])
        
        # Name and percentage
        draw.text((left_x + 72, card_y + 14), sc["name"], fill=sc["color"], font=font_badge)
        draw.text((left_x + left_w - 120, card_y + 14), sc["pct"], fill=sc["color"], font=font_badge)

        draw.text((left_x + 72, card_y + 44), f"Số lượng: {sc['count']}", fill=text_primary, font=font_tree_branch)
        draw.text((left_x + 72, card_y + 74), sc["desc"], fill=text_secondary, font=font_tree_desc)
        card_y += 125

    # Right Card: Full Directory Tree Structure (Width: 1530px)
    right_x = left_x + left_w + 50
    right_w = width - right_x - 70
    draw.rounded_rectangle([right_x, top_y, right_x + right_w, top_y + content_h], radius=20, fill=card_bg, outline=card_border, width=2)

    # Right Card Header
    r_head = "2. SƠ ĐỒ CÂY THƯ MỤC CHUẨN HÓA (VN_REAL_FOOD_SPLIT /)"
    draw.text((right_x + 40, top_y + 35), r_head, fill=folder_root, font=font_box_title)

    # Root Directory Box
    tree_box_y = top_y + 85
    draw.rounded_rectangle([right_x + 35, tree_box_y, right_x + right_w - 35, top_y + content_h - 35], radius=14, fill=inner_bg, outline=card_border, width=1)

    # Root Folder Icon + Text
    rx = right_x + 65
    ry = tree_box_y + 30
    draw_folder_icon(draw, rx, ry, size=34, color=folder_root)
    draw.text((rx + 48, ry - 3), "VN_Real_Food_Split/  (dataset_split/)", fill=text_primary, font=font_tree_root)
    
    tag_root = "THƯ MỤC GỐC ĐÃ CHIA TẬP"
    draw.rounded_rectangle([rx + 560, ry, rx + 800, ry + 32], radius=8, fill=(234, 88, 12))
    draw.text((rx + 575, ry + 5), tag_root, fill=(255, 255, 255), font=font_badge)

    # Main Branches: train/, val/, test/
    # We will display 3 big columns inside the tree box for train, val, test!
    col_w = (right_w - 110) // 3
    col_gap = 20
    branch_top_y = ry + 75

    columns_data = [
        {
            "folder": "train/",
            "title": "TẬP HUẤN LUYỆN (TRAIN)",
            "count": "2.004 ảnh (70%)",
            "color": badge_train,
            "classes": [
                ("banh_bo/", "210 ảnh"),
                ("banh_bot_loc/", "210 ảnh"),
                ("banh_cong/", "162 ảnh"),
                ("banh_da_lon/", "210 ảnh"),
                ("banh_khot/", "210 ảnh"),
                ("banh_mi/", "210 ảnh"),
                ("banh_tai_heo/", "210 ảnh"),
                ("banh_tieu/", "200 ảnh"),
                ("banh_trung_thu/", "172 ảnh"),
                ("banh_xeo/", "210 ảnh"),
            ],
            "sample_file": "├── banh_bo_001.jpg\n└── ... (.jpg, .png)"
        },
        {
            "folder": "val/",
            "title": "TẬP KIỂM ĐỊNH (VAL)",
            "count": "428 ảnh (15%)",
            "color": badge_val,
            "classes": [
                ("banh_bo/", "45 ảnh"),
                ("banh_bot_loc/", "45 ảnh"),
                ("banh_cong/", "34 ảnh"),
                ("banh_da_lon/", "45 ảnh"),
                ("banh_khot/", "45 ảnh"),
                ("banh_mi/", "45 ảnh"),
                ("banh_tai_heo/", "45 ảnh"),
                ("banh_tieu/", "42 ảnh"),
                ("banh_trung_thu/", "37 ảnh"),
                ("banh_xeo/", "45 ảnh"),
            ],
            "sample_file": "├── banh_bo_val01.jpg\n└── ... (.jpg, .png)"
        },
        {
            "folder": "test/",
            "title": "TẬP KIỂM THỬ (TEST)",
            "count": "433 ảnh (15%)",
            "color": badge_test,
            "classes": [
                ("banh_bo/", "45 ảnh"),
                ("banh_bot_loc/", "45 ảnh"),
                ("banh_cong/", "36 ảnh"),
                ("banh_da_lon/", "45 ảnh"),
                ("banh_khot/", "45 ảnh"),
                ("banh_mi/", "45 ảnh"),
                ("banh_tai_heo/", "45 ảnh"),
                ("banh_tieu/", "44 ảnh"),
                ("banh_trung_thu/", "38 ảnh"),
                ("banh_xeo/", "45 ảnh"),
            ],
            "sample_file": "├── banh_bo_test01.jpg\n└── ... (.jpg, .png)"
        }
    ]

    # Connecting tree line from root to columns
    draw.line([(rx + 17, ry + 36), (rx + 17, branch_top_y + 15)], fill=tree_line_color, width=3)
    draw.line([(rx + 17, branch_top_y + 15), (right_x + right_w - 90, branch_top_y + 15)], fill=tree_line_color, width=3)

    for i, col in enumerate(columns_data):
        cx = right_x + 55 + i * (col_w + col_gap)
        cy = branch_top_y + 35

        # Drop line from horizontal branch
        draw.line([(cx + 25, branch_top_y + 15), (cx + 25, cy + 10)], fill=tree_line_color, width=3)

        # Column Container Box
        c_h = top_y + content_h - 35 - cy - 25
        draw.rounded_rectangle([cx, cy, cx + col_w, cy + c_h], radius=12, fill=card_bg, outline=card_border, width=1)

        # Top banner for split
        draw.rounded_rectangle([cx, cy, cx + col_w, cy + 60], radius=12, fill=col["color"])
        draw.rectangle([cx, cy + 45, cx + col_w, cy + 60], fill=col["color"]) # square bottom corners

        draw_folder_icon(draw, cx + 18, cy + 16, size=28, color=(255, 255, 255))
        draw.text((cx + 56, cy + 12), col["folder"], fill=(255, 255, 255), font=font_tree_root)
        draw.text((cx + 180, cy + 16), col["count"], fill=(255, 255, 255), font=font_badge)

        # Class list items
        item_y = cy + 75
        for cls_idx, (c_name, c_cnt) in enumerate(col["classes"]):
            is_last = (cls_idx == len(col["classes"]) - 1)
            prefix = "└── " if is_last else "├── "
            
            # Tree prefix
            draw.text((cx + 20, item_y), prefix, fill=tree_line_color, font=font_tree_leaf)
            # Folder icon
            draw_folder_icon(draw, cx + 70, item_y + 2, size=18, color=folder_color)
            # Folder name
            draw.text((cx + 96, item_y - 2), c_name, fill=text_primary, font=font_tree_leaf)
            # Count badge
            draw.text((cx + col_w - 110, item_y), c_cnt, fill=text_secondary, font=font_tree_desc)

            item_y += 50

        # Sample file box at bottom
        file_box_y = cy + c_h - 115
        draw.rounded_rectangle([cx + 15, file_box_y, cx + col_w - 15, file_box_y + 95], radius=8, fill=inner_bg, outline=card_border, width=1)
        
        draw_file_icon(draw, cx + 25, file_box_y + 15, size=20, color=(14, 165, 233))
        draw.text((cx + 52, file_box_y + 12), "Cấu trúc tệp ảnh bên trong:", fill=text_accent, font=font_badge)
        draw.text((cx + 52, file_box_y + 40), col["sample_file"].split('\n')[0], fill=text_secondary, font=font_tree_leaf)
        draw.text((cx + 52, file_box_y + 64), col["sample_file"].split('\n')[1], fill=text_secondary, font=font_tree_leaf)

    # 3. Overall Footer
    foot_text = "Hình 2.2: Cấu trúc phân cấp cây thư mục dữ liệu đạt chuẩn YOLOv8 & PyTorch ImageFolder  |  Định dạng ảnh: RGB (.jpg, .png)  |  Resize chuẩn hóa: 448x448 px"
    fb = draw.textbbox((0, 0), foot_text, font=font_footer)
    fw = fb[2] - fb[0]
    draw.text(((width - fw) // 2, height - 65), foot_text, fill=text_secondary, font=font_footer)

    img.save(output_path, quality=95)
    print(f"Đã xuất thành công: {output_path} ({width}x{height}px)")

if __name__ == "__main__":
    create_directory_structure_figure(dark_mode=False, output_path=r"C:\XLA\static\img\hinh_2_2_directory_structure_white.png")
    create_directory_structure_figure(dark_mode=True, output_path=r"C:\XLA\static\img\hinh_2_2_directory_structure_dark.png")
