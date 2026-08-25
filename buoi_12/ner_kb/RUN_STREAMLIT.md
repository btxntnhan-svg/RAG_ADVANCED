# Hướng dẫn chạy Streamlit App

## Cài đặt thư viện

Trước tiên, cài đặt Streamlit và Plotly nếu chưa có:

```bash
cd "c:\Users\Win10-64\Desktop\Buổi 12\ner_kb"
.\.venv\Scripts\pip install streamlit plotly
```

Hoặc cài tất cả từ requirements.txt:

```bash
.\.venv\Scripts\pip install -r requirements.txt
```

---

## Chạy App

```bash
.\.venv\Scripts\streamlit run streamlit_app.py
```

App sẽ mở trên trình duyệt tại: http://localhost:8501

---

## Các trang chính

### 1. **Dashboard** 📊
- Thống kê tổng số node, relationship
- Biểu đồ phân bố node theo label
- Biểu đồ relationship theo type
- Số document theo cơ quan ban hành

### 2. **Documents** 📄
- Tìm kiếm document theo ID hoặc tiêu đề
- Xem chi tiết từng document
- Xem các liên kết graph của document
- Hiển thị preview nội dung

### 3. **Entities** 🏢
- Duyệt các entity (CoQuan, NguoiKy, DoiTuongApDung, LinhVuc)
- Lọc theo loại entity
- Xem thống kê entity
- Biểu đồ phân bố entity

### 4. **Relationships** 🔗
- Duyệt tất cả relationship
- Lọc theo type hoặc method
- Xem validation report
- Biểu đồ relationship by type

### 5. **Graph Explorer** 🕸️
- Chạy pre-built Cypher queries
- Viết custom Cypher query
- Download kết quả CSV
- Các sample query có sẵn:
  - All Documents
  - Document → NguoiKy
  - Document → CoQuan
  - Document → DoiTuongApDung
  - Document → LinhVuc
  - Node count by label
  - Relationship count by type

### 6. **Pipeline** 🔄
- Chạy full pipeline từ UI
- Xem real-time output
- Download log

### 7. **Statistics** 📈
- Xem size của các file CSV
- Row count của mỗi file
- Thống kê chi tiết từng file

---

## Troubleshooting

### Lỗi: "Neo4j connection failed"
- Kiểm tra `.env` file có đúng config không
- Kiểm tra Neo4j service đang chạy trên port 7687
- Kiểm tra username/password trong `.env`

### Lỗi: "File not found"
- Kiểm tra working directory phải là folder `ner_kb`
- Kiểm tra các file CSV đã được tạo chưa (chạy pipeline trước)

### Streamlit bị lag
- Kiểm tra internet connection
- Kiểm tra resources (RAM, CPU)
- Restart Streamlit

---

## Shortcut

- **Ctrl+C:** Stop Streamlit
- **R:** Reload app
- **S:** Save app state (nếu config)

---

## Deployment (Optional)

Nếu muốn deploy online:

```bash
streamlit run streamlit_app.py --logger.level=error
```

Hoặc dùng Streamlit Cloud: https://streamlit.io/cloud

---

## Customization

Sửa `streamlit_app.py` để:
- Thêm page mới
- Thay đổi UI layout
- Thêm filter/search tùy chỉnh
- Thêm query mới

**Note:** Streamlit tự reload khi file thay đổi.
