# BÁO CÁO PHỤ THUỘC VÀ TÁI SỬ DỤNG DỮ LIỆU/CODE BUỔI 16 (DEPENDENCY REPORT)

- **Ngày thực hiện**: 2026-08-25
- **Môi trường thực thi**: `buoi_17/`
- **Nguồn dữ liệu tham chiếu**: `../buoi_16/data/processed/`

---

## 1. Kiểm tra Dữ liệu Đầu vào (Source Data Audit)

| Tiêu chí | `chunks_secure.csv` | `chunks_normalized.csv` | Kết quả đối chiếu |
| :--- | :--- | :--- | :--- |
| **Đường dẫn tệp** | `../buoi_16/data/processed/chunks_secure.csv` | `../buoi_16/data/processed/chunks_normalized.csv` | Tồn tại & Đọc thành công |
| **Số lượng dòng (Chunks)** | 15 dòng | 15 dòng | **KHỚP 100%** |
| **Số lượng cột** | 13 cột | 11 cột | Khác biệt 2 cột bảo mật |
| **Các trường thông tin bắt buộc** | `chunk_id`, `document_id`, `text`, `source_file`, `title`, `document_type`, `effective_date`, `status`, `citation_code`, `issued_date`, `source_document_id`, `security_class`, `allowed_roles` | `chunk_id`, `document_id`, `text`, `source_file`, `title`, `document_type`, `effective_date`, `status`, `citation_code`, `issued_date`, `source_document_id` | Có đầy đủ các trường yêu cầu |

### So sánh & Khẳng định mối quan hệ Dữ liệu:
`chunks_secure.csv` = `chunks_normalized.csv` + `security_class` + `allowed_roles`.
- Toàn bộ 11 cột dữ liệu cơ sở của hai file hoàn toàn trùng khớp 100% trên từng dòng chunk.
- Tệp `chunks_secure.csv` bổ sung thêm trường `security_class` (phân loại bảo mật: HR, Risk, General) và `allowed_roles` (danh sách vai trò được phép xem: Admin, HR, Staff, Guest).

---

## 2. Kiểm toán Code `SecureRetriever` (Secure Retriever Audit)

- **Vị trí File/Module**: `buoi_14/src/secure_retriever.py` (Tham chiếu trực tiếp cho Buổi 16)
- **Class / Hàm chính**: `SecureRetriever`, phương thức `retrieve(query, user_roles, method='hybrid', top_k=5, candidate_k=20)`
- **Tham số Vai trò Đầu vào (Input Roles)**: `user_roles` (chuỗi danh sách vai trò dạng `list[str]` hoặc `tuple[str, ...]`, ví dụ: `["Guest"]`, `["HR", "Staff"]`).
- **Cấu trúc Kết quả Trả về (Output Format)**: Danh sách `list[dict]` chứa đầy đủ các trường:
  - `rank`: Thứ tự xếp hạng kết quả
  - `chunk_id`: Mã định danh chunk
  - `document_id`: Mã định danh văn bản
  - `text`: Nội dung văn bản
  - `score`: Điểm tương đồng / xếp hạng
  - `citation`: Trích dẫn văn bản quy định
  - `retrieval_method`: Phương thức tìm kiếm (BM25, Dense, Hybrid, Rerank, Graph)
  - `allowed_roles`: Danh sách vai trò được phép truy cập
- **Cơ chế Lọc Bảo mật (Pre-filtering)**: **LỌC TRƯỚC TRUY VẤN (Filter BEFORE Retrieval)**.
  - Hàm `_filter(user_roles)` được kích hoạt ngay đầu phương thức `retrieve()`.
  - Chỉ các chunks thỏa mãn `set(allowed_roles) ∩ set(user_roles)` mới được đưa vào quá trình tính toán Lexical (BM25), Semantic (Dense), Fusion (RRF) hay Reranking.
  - Đảm bảo 100% dữ liệu nhạy cảm không bị rò rỉ vào pha tính toán candidate.
- **Bảo toàn Định danh & Metadata**: Các trường `document_id`, `chunk_id`, `citation`, `title` được giữ nguyên vẹn 100% trong kết quả trả về.

---

## 3. Kế hoạch Tái sử dụng (Reuse Plan)

1. **Giữ nguyên trạng Code Buổi 16**: Không tạo policy mới, không viết lại retriever mới, không sửa các file dữ liệu hay source code của Buổi 16.
2. **Adapter Chuẩn hóa Output (nếu cần)**: Tạo `buoi_17/scripts/secure_retrieval_adapter.py` đóng vai trò là một wrapper nhẹ gọi tới `SecureRetriever` và chuẩn hóa key output nếu Buổi 17 yêu cầu định dạng khác.

---

## 4. Kết luận

SOURCE DATA: PASS
RBAC DATA AVAILABLE: YES
SECURE RETRIEVER REUSABLE: YES
REUSE PLAN: Tái sử dụng trực tiếp class `SecureRetriever` từ `buoi_14/src/secure_retriever.py` qua một Adapter nhẹ `buoi_17/scripts/secure_retrieval_adapter.py` để đảm bảo tính sẵn sàng và an toàn bảo mật dữ liệu tuyệt đối cho Buổi 17.
