import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def generate_chart(dark_mode=False, output_path="thong_ke_du_lieu.png"):
    classes = [
        "Bánh Bò", "Bánh Bột Lọc", "Bánh Cống", "Bánh Da Lợn", "Bánh Khọt",
        "Bánh Mì", "Bánh Tai Heo", "Bánh Tiêu", "Bánh Trung Thu", "Bánh Xèo"
    ]
    class_ids = [
        "banh_bo", "banh_bot_loc", "banh_cong", "banh_da_lon", "banh_khot",
        "banh_mi", "banh_tai_heo", "banh_tieu", "banh_trung_thu", "banh_xeo"
    ]
    train_counts = [210, 210, 162, 210, 210, 210, 210, 200, 172, 210]
    val_counts   = [ 45,  45,  34,  45,  45,  45,  45,  42,  37,  45]
    test_counts  = [ 45,  45,  36,  45,  45,  45,  45,  44,  38,  45]
    total_counts = [t + v + te for t, v, te in zip(train_counts, val_counts, test_counts)]

    # Theme colors
    if dark_mode:
        bg_fig = '#0f172a'       # Slate 900
        bg_ax = '#1e293b'        # Slate 800
        text_color = '#f8fafc'   # Slate 50
        text_sub = '#94a3b8'     # Slate 400
        grid_color = '#334155'   # Slate 700
        color_train = '#10b981'  # Emerald 500
        color_val = '#3b82f6'    # Blue 500
        color_test = '#a855f7'   # Purple 500
        box_edge = '#475569'
    else:
        bg_fig = '#f8fafc'       # Slate 50
        bg_ax = '#ffffff'        # White
        text_color = '#0f172a'   # Slate 900
        text_sub = '#64748b'     # Slate 500
        grid_color = '#e2e8f0'   # Slate 200
        color_train = '#059669'  # Emerald 600
        color_val = '#2563eb'    # Blue 600
        color_test = '#9333ea'   # Purple 600
        box_edge = '#cbd5e1'

    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']
    plt.rcParams['axes.edgecolor'] = box_edge
    plt.rcParams['axes.linewidth'] = 1.2

    fig = plt.figure(figsize=(19, 10), facecolor=bg_fig, dpi=180)
    gs = fig.add_gridspec(2, 3, width_ratios=[2.2, 1, 1], height_ratios=[1, 1],
                         left=0.06, right=0.96, top=0.88, bottom=0.09, wspace=0.28, hspace=0.32)

    # 1. Main Subplot: Stacked Horizontal Bar Chart (Train, Val, Test per Class)
    ax1 = fig.add_subplot(gs[:, 0], facecolor=bg_ax)
    y_pos = np.arange(len(classes))
    bar_height = 0.58

    b_train = ax1.barh(y_pos, train_counts, height=bar_height, label='Train (70%)', color=color_train, edgecolor=bg_ax, alpha=0.95)
    b_val = ax1.barh(y_pos, val_counts, left=train_counts, height=bar_height, label='Val (15%)', color=color_val, edgecolor=bg_ax, alpha=0.95)
    left_test = [t + v for t, v in zip(train_counts, val_counts)]
    b_test = ax1.barh(y_pos, test_counts, left=left_test, height=bar_height, label='Test (15%)', color=color_test, edgecolor=bg_ax, alpha=0.95)

    # Value annotations on bars
    for idx, (tot, cid) in enumerate(zip(total_counts, class_ids)):
        ax1.text(tot + 6, idx, f"{tot} ảnh", va='center', ha='left', fontsize=11, fontweight='bold', color=text_color)
        ax1.text(5, idx, f"({cid})", va='center', ha='left', fontsize=9, color='#ffffff', alpha=0.85, style='italic')

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(classes, fontsize=12, fontweight='bold', color=text_color)
    ax1.invert_yaxis()  # Top-down order
    ax1.set_xlim(0, 355)
    ax1.set_xlabel('Số lượng ảnh mẫu (Ảnh)', fontsize=12, fontweight='bold', color=text_color, labelpad=10)
    ax1.set_title('PHÂN BỔ SỐ LƯỢNG ẢNH THEO 10 LỚP MÓN ĂN & TẬP CHIA (70/15/15)', fontsize=13, fontweight='bold', color=text_color, pad=14)
    ax1.grid(axis='x', color=grid_color, linestyle='--', alpha=0.7)
    ax1.tick_params(colors=text_color, labelsize=11)
    ax1.legend(loc='lower right', frameon=True, facecolor=bg_ax, edgecolor=box_edge, fontsize=10, labelcolor=text_color)

    # 2. Subplot 2: Overall Split Proportion (Donut Chart)
    ax2 = fig.add_subplot(gs[0, 1], facecolor=bg_ax)
    total_train = sum(train_counts)
    total_val = sum(val_counts)
    total_test = sum(test_counts)
    split_sizes = [total_train, total_val, total_test]
    split_labels = [f"Train\n{total_train} ảnh\n(69.9%)", f"Val\n{total_val} ảnh\n(14.9%)", f"Test\n{total_test} ảnh\n(15.1%)"]
    split_colors = [color_train, color_val, color_test]

    wedges, texts, autotexts = ax2.pie(
        split_sizes, labels=split_labels, colors=split_colors, autopct='%1.1f%%',
        startangle=140, pctdistance=0.75,
        textprops={'color': text_color, 'fontsize': 10, 'fontweight': 'medium'},
        wedgeprops=dict(width=0.45, edgecolor=bg_fig, linewidth=2)
    )
    for at in autotexts:
        at.set_color('#ffffff')
        at.set_fontweight('bold')
        at.set_fontsize(10)
    ax2.set_title('TỶ LỆ PHÂN CHIA TỔNG THỂ\n(Tổng: 2.865 ảnh)', fontsize=12, fontweight='bold', color=text_color, pad=10)

    # 3. Subplot 3: File Format & Channels
    ax3 = fig.add_subplot(gs[0, 2], facecolor=bg_ax)
    fmt_labels = ['JPEG / JPG\n(2.865 ảnh)', 'Khác (0)']
    fmt_sizes = [2865, 0.0001]
    wedges2, texts2 = ax3.pie(
        fmt_sizes, labels=fmt_labels, colors=['#ea580c', '#64748b'],
        startangle=90, textprops={'color': text_color, 'fontsize': 10, 'fontweight': 'medium'},
        wedgeprops=dict(width=0.45, edgecolor=bg_fig, linewidth=2)
    )
    ax3.set_title('ĐỊNH DẠNG TỆP & KHÔNG GIAN MÀU\n(100% Ảnh RGB 3 Kênh)', fontsize=12, fontweight='bold', color=text_color, pad=10)

    # 4. Subplot 4: Resolution & Image Quality Metrics
    ax4 = fig.add_subplot(gs[1, 1:], facecolor=bg_ax)
    metrics = [
        "Độ phân giải rộng (Width)", "Độ phân giải cao (Height)", 
        "Kích thước chuẩn hóa YOLO", "Kích thước chuẩn hóa CNN"
    ]
    avg_vals = [751.5, 576.1, 448.0, 224.0]
    min_vals = [75.0, 88.0, 448.0, 224.0]
    max_vals = [4288.0, 4095.0, 448.0, 224.0]

    x_idx = np.arange(len(metrics))
    w_bar = 0.35

    b1 = ax4.bar(x_idx - w_bar/2, avg_vals, width=w_bar, label='Kích thước trung bình / Chuẩn hóa (px)', color='#f97316', edgecolor=bg_ax, alpha=0.95)
    b2 = ax4.bar(x_idx + w_bar/2, max_vals, width=w_bar, label='Kích thước tối đa gốc (px)', color='#38bdf8' if dark_mode else '#0284c7', edgecolor=bg_ax, alpha=0.95)

    for b in b1:
        h = b.get_height()
        ax4.text(b.get_x() + b.get_width()/2, h + 60, f"{h:.0f}px", ha='center', va='bottom', fontsize=10, fontweight='bold', color=text_color)
    for b in b2:
        h = b.get_height()
        ax4.text(b.get_x() + b.get_width()/2, h + 60, f"{h:.0f}px", ha='center', va='bottom', fontsize=10, fontweight='bold', color=text_color)

    ax4.set_xticks(x_idx)
    ax4.set_xticklabels(metrics, fontsize=11, fontweight='medium', color=text_color)
    ax4.set_ylim(0, 5000)
    ax4.set_ylabel('Điểm ảnh (Pixels)', fontsize=11, fontweight='bold', color=text_color)
    ax4.set_title('THỐNG KÊ ĐỘ PHÂN GIẢI ẢNH GỐC VÀ CHUẨN HÓA ĐẦU VÀO MÔ HÌNH', fontsize=12, fontweight='bold', color=text_color, pad=10)
    ax4.grid(axis='y', color=grid_color, linestyle='--', alpha=0.7)
    ax4.tick_params(colors=text_color)
    ax4.legend(loc='upper right', frameon=True, facecolor=bg_ax, edgecolor=box_edge, fontsize=10, labelcolor=text_color)

    # Master Figure Title & Subtitle
    fig.suptitle('BẢNG THỐNG KÊ VÀ PHÂN BỐ TẬP DỮ LIỆU NHẬN DIỆN 10 MÓN ĂN VIỆT NAM',
                 fontsize=18, fontweight='bold', color=text_color, y=0.97)
    fig.text(0.5, 0.925,
             'Tổng mẫu: 2.865 ảnh | Phân chia sạch 70% Train (2.004) - 15% Val (428) - 15% Test (433) | 100% Ảnh RGB 3 Kênh',
             ha='center', fontsize=12, color=text_sub)

    plt.savefig(output_path, dpi=180, facecolor=bg_fig, bbox_inches='tight')
    plt.close()
    print(f"Đã xuất biểu đồ thống kê: {output_path}")

if __name__ == "__main__":
    generate_chart(dark_mode=False, output_path=r"C:\XLA\static\img\thong_ke_du_lieu_white.png")
    generate_chart(dark_mode=True, output_path=r"C:\XLA\static\img\thong_ke_du_lieu_dark.png")
