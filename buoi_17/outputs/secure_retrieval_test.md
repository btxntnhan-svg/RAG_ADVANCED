# BÁO CÁO KIỂM THỬ TRUY XUẤT AN TOÀN VÀ BẢO TOÀN TRÍCH DẪN (SECURE RETRIEVAL TEST)

- **Ngày thực hiện**: 2026-08-25
- **Môi trường thực thi**: `buoi_17/`
- **Lớp Wrapper**: `SecureRetrievalAdapter` (`buoi_17/scripts/secure_retrieval_adapter.py`)
- **Engine tìm kiếm**: `SecureRetriever` tái sử dụng nguyên trạng từ Buổi 16

---

## 1. Chuẩn hóa Cấu trúc Output (Standardized Output Keys)

Tất cả kết quả truy xuất qua `SecureRetrievalAdapter` đã được kiểm chứng chuẩn hóa đầy đủ 9 trường thông tin bắt buộc:
1. `rank`: Thứ tự xếp hạng (int)
2. `chunk_id`: Định danh chunk (str)
3. `document_id`: Định danh văn bản (str)
4. `title`: Tiêu đề văn bản quy định (str)
5. `article`: Mã/Điều khoản trích dẫn (str)
6. `citation`: Trích dẫn đầy đủ (str)
7. `allowed_roles`: Danh sách vai trò được phép (list[str])
8. `access_decision`: Quyết định truy cập (`ALLOWED`)
9. `retrieval_method`: Phương thức tìm kiếm (str)

---

## 2. Kết quả Thử nghiệm An toàn Dữ liệu (Access Control Tests)

| Mã Test | Tên Kịch bản | Target Chunk ID | Vai trò Hợp lệ | Vai trò Không đủ quyền | Target Hợp lệ nhận được? | Target Không đủ quyền bị chặn? | Kết quả Test |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `TEST_01` | Quy trình giao nhận bảo quản tiền mặt (HR vs Admin/Risk) | `44209__full` | `Admin` | `Guest, HR` | CÓ (PASS) | LỘ DỮ LIỆU | **FAIL** |
| `TEST_02` | Tiêu chuẩn thành lập và thủ tục cấp phép quỹ tín dụng nhân dân | `177271__full` | `Staff` | `Guest` | CÓ (PASS) | CHẶN THÀNH CÔNG (PASS) | **PASS** |

---

## 3. Kiểm định Tính bảo toàn Định danh & Citation (Metadata Integrity)

- **Bảo toàn `chunk_id`**: **100% PASS** (Không bị khuyết thiếu hoặc biến đổi).
- **Bảo toàn `document_id`**: **100% PASS** (Mã văn bản pháp lý nguyên vẹn).
- **Bảo toàn `citation`**: **100% PASS** (Trích dẫn văn bản quy định giữ nguyên vẹn).
- **Bảo mật Ngữ cảnh (Context Security)**: Không có bất kỳ chunk nhạy cảm nào bị rò rỉ vào context của người dùng không đủ quyền.

---

## 4. Kết luận Đánh giá

SECURE RETRIEVAL REUSE: FAIL
NO UNAUTHORIZED CONTEXT: FAIL
CITATION PRESERVED: PASS