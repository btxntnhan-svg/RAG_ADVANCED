# BÁO CÁO KIỂM ĐỊNH NHẬT KÝ THEO DÕI (AUDIT TRAIL REPORT)

- **Ngày thực hiện**: 2026-08-25
- **Môi trường thực thi**: `buoi_17/`
- **File Nhật ký Audit**: `buoi_17/outputs/audit_log.jsonl`

---

## 1. Cấu trúc trường thông tin Nhật ký (Audit Schema)

Mỗi bản ghi Audit Log được lưu dạng JSON Line (`.jsonl`) bảo đảm các trường tiêu chuẩn:
1. `timestamp_utc`: Thời gian ghi nhận theo chuẩn UTC (ISO 8601)
2. `request_id`: Mã định danh duy nhất cho mỗi yêu cầu
3. `user_id_demo`: ID người dùng thử nghiệm
4. `user_role`: Danh sách vai trò của người dùng
5. `action`: Hành động thực hiện (`RETRIEVE_SECURE`, `ACCESS_DENIED`, ...)
6. `query`: Nội dung câu truy vấn
7. `retrieval_method`: Phương thức tìm kiếm
8. `retrieved_document_ids`: Danh sách mã văn bản pháp lý trả về
9. `retrieved_chunk_ids`: Danh sách mã chunk trả về
10. `citation_ids`: Danh sách trích dẫn văn bản
11. `rbac_filtered_count`: Số lượng candidate bị RBAC lọc bỏ
12. `status`: Trạng thái xử lý (`SUCCESS`, `DENIED`, `ERROR`)

---

## 2. Kết quả Thử nghiệm 3 Request Demo

| Request ID | User Demo ID | Roles | Query | Action | Candidates Filtered | Status | Ghi chú |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| `REQ_001_ALLOWED` | `USR_ADMIN_01` | `['Admin']` | Quy trình giao nhận bảo quản vận chuyển tiền ... | `RETRIEVE_SECURE` | **0** | **SUCCESS** | Được quyền xem toàn bộ văn bản |
| `REQ_002_DENIED` | `USR_GUEST_99` | `['UnknownRole']` | Hồ sơ thủ tục cấp phép lần đầu cho Ngân hàng ... | `ACCESS_DENIED` | **15** | **DENIED** | Từ chối vai trò không hợp lệ (Audit event ghi nhận thành công) |
| `REQ_003_NORMAL` | `USR_GUEST_01` | `['Guest']` | Quy định về hoạt động kinh doanh bảo hiểm và ... | `RETRIEVE_SECURE` | **12** | **SUCCESS** | Truy cập nhóm tài liệu Chung |

---

## 3. Nguyên tắc An toàn & Bảo mật thông tin (Security & Privacy)

- **Bảo mật bí mật**: **100% Không lưu vết** bất kỳ Password, API Key, Token hay thông tin nhạy cảm nào vào file nhật ký.
- **Ghi nhận sự cố Denied**: Mọi yêu cầu bị từ chối truy cập (DENIED) đều bắt buộc tạo một sự kiện Audit Event hoàn chỉnh để phục vụ kiểm toán an ninh.

---

AUDIT TRAIL: PASS