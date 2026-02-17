# Ứng dụng quản lý văn bản (Streamlit)

Ứng dụng nhỏ viết bằng **Python + Streamlit** giúp:

- Quản lý, lưu trữ văn bản/tài liệu
- Tải lên tệp từ máy
- Tìm kiếm theo tiêu đề, mô tả, tên tệp, từ khóa
- Xem nhanh nội dung một số loại file (txt, md, hình ảnh)
- Tải xuống lại file hoặc xóa văn bản

## 1. Cài đặt

Mở **PowerShell** tại thư mục:

```bash
cd "c:\Users\tmtrd\OneDrive\Desktop\Practice Python\04. App4"
```

Tạo môi trường ảo (khuyến nghị, có thể bỏ qua nếu bạn quen):

```bash
python -m venv .venv
.venv\Scripts\activate
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

## 2. Chạy ứng dụng

Trong thư mục dự án, chạy:

```bash
streamlit run app.py
```

Trình duyệt sẽ mở tại địa chỉ dạng `http://localhost:8501` với giao diện ứng dụng.

## 3. Cách sử dụng

- Ở **thanh bên trái**:
  - Chọn tệp để tải lên
  - Nhập tiêu đề (nếu bỏ trống sẽ dùng luôn tên file)
  - Nhập mô tả (tuỳ chọn)
  - Nhập từ khóa, phân cách bằng dấu phẩy (ví dụ: `hợp đồng, khách hàng, 2025`)
  - Bấm nút **“Lưu văn bản”**

- Ở **phần chính giữa**:
  - Xem **danh sách văn bản** đã lưu
  - Tìm kiếm theo từ khóa (tiêu đề, mô tả, tên file, tags)
  - Lọc theo từng từ khóa cụ thể
  - Mở từng văn bản (expander) để:
    - Xem thông tin chi tiết
    - Xem nội dung nhanh (txt, md, hình ảnh)
    - Tải xuống lại file
    - Xóa văn bản

## 4. Lưu trữ dữ liệu

- File được lưu vào thư mục `uploaded_documents/` (tự tạo khi chạy ứng dụng lần đầu).
- Thông tin văn bản (tiêu đề, mô tả, đường dẫn file, tags, thời gian…) lưu trong file `documents_meta.json` cùng thư mục dự án.

