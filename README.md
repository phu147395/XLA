# AI Food Vision - Hệ Thống Thị Giác Máy Tính & Nhận Diện Món Ăn

Ứng dụng web tương tác liên kết trực tiếp với mô hình Trí Tuệ Nhân Tạo (YOLOv8 & PyTorch) từ bài toán Xử Lý Ảnh (XLA), hỗ trợ đa phương tiện với 3 chế độ:

1. 📸 **Tải lên Hình ảnh (Image Upload)**: Kéo thả hoặc chọn ảnh từ máy, nhận diện tức thì tên món ăn, tỷ lệ tin cậy Top-1 / Top-5, thông tin dinh dưỡng và trực quan hóa kết quả.
2. 🎬 **Tải lên Video (Video Upload)**: Tải video định dạng MP4/AVI/MOV, phân tích từng khung hình bằng mô hình AI, tự động vẽ hộp/nhãn tên món ăn và xuất video kết quả cho phép xem & tải về.
3. 📹 **Camera / Webcam Trực tiếp (Live Camera)**: Bật webcam máy tính hoặc camera ngoài, phát hiện món ăn theo thời gian thực (Real-time Detection), hỗ trợ chụp ảnh nhanh (snapshot) và đọc tên món ăn bằng giọng nói AI (Text-to-Speech).

---

## 📁 Cấu Trúc Dự Án

```text
C:\XLA\
│
├── app.py                  # Máy chủ FastAPI Backend (Xử lý API nhận diện ảnh, video, camera)
├── best.pt                 # Trọng số mô hình YOLO đã huấn luyện
├── food (4).ipynb          # Jupyter Notebook huấn luyện và kiểm thử mô hình
├── run.bat                 # File thực thi 1-click khởi động ứng dụng web
│
├── templates/
│   └── index.html          # Giao diện người dùng Web hiện đại (TailwindCSS, Lucide Icons)
│
├── static/
│   ├── css/
│   │   └── style.css       # Hiệu ứng giao diện, thanh cuộn, animations
│   ├── js/
│   │   └── app.js          # Logic phía client (xử lý camera, video, ajax, audio)
│   ├── samples/            # Thư mục ảnh mẫu để kiểm thử nhanh
│   └── outputs/            # Thư mục chứa video kết quả sau khi AI xử lý
│
└── uploads/                # Thư mục tạm lưu video và hình ảnh tải lên
```

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Khởi động Web Server
- Cách 1: Nhấp đúp chuột vào file `run.bat`.
- Cách 2: Mở PowerShell / Command Prompt tại thư mục `C:\XLA` và chạy lệnh:
  ```powershell
  python app.py
  ```

### 2. Mở trình duyệt Web
Truy cập địa chỉ:
👉 **[http://localhost:8000](http://localhost:8000)** (hoặc `http://127.0.0.1:8000`)

---

## 🌟 Chi Tiết Tính Năng

### 1. Tab Hình Ảnh
- Kéo thả bất kỳ tệp ảnh món ăn (JPG, PNG, WEBP).
- Có sẵn các nút ảnh mẫu (`Bánh Mì`, `Bún`, `Gỏi Cuốn`, `Bột Chiên`, `Phở`) để kiểm tra nhanh chỉ với 1 cú click.
- Hiển thị thanh tiến trình xác suất (Probability bars), lượng calo ước tính và mô tả món ăn.

### 2. Tab Video
- Tải lên video món ăn bất kỳ.
- Cho phép chỉnh "Tốc độ lấy mẫu" (xử lý mỗi 1, 2 hoặc 5 khung hình) để cân bằng giữa tốc độ và độ mượt mà.
- Trình phát video tích hợp phát lại video đã được AI gán nhãn nhận diện.

### 3. Tab Camera Trực Tiếp
- Lựa chọn nguồn camera (Webcam tích hợp, Webcam USB ngoài).
- Nút "Bật/Tắt Camera" an toàn và mượt mà.
- Tự động nhận diện thời gian thực với khung ngắm HUD và bảng xếp hạng xác suất động.
- Tính năng "Chụp Ảnh Nhanh" (Snapshot) để lưu lại khoảnh khắc nhận diện.
- Tùy chọn "Đọc tên món (Giọng nói AI)" phát âm thanh tiếng Việt khi phát hiện món ăn.
