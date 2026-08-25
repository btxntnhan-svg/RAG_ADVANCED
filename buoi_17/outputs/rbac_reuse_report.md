# BÁO CÁO TÁI SỬ DỤNG VÀ KIỂM THỬ RBAC (RBAC REUSE REPORT)

- **Ngày thực hiện**: 2026-08-25
- **Môi trường thực thi**: `buoi_17/`
- **Nguồn dữ liệu**: `C:\Users\Win10-64\Desktop\RAG_ADVANCED\buoi_16\data\processed\chunks_secure.csv` (15 chunks)

---

## 1. Thống kê Danh sách Vai trò (Role Analysis)

- **Các vai trò xuất hiện trong dữ liệu**: `Admin, Guest, HR, Staff`
- **Phân bổ số lượng Chunk được phép truy cập theo từng Vai trò**:
  - `Admin`: **15** / 15 chunks
  - `Guest`: **3** / 15 chunks
  - `HR`: **5** / 15 chunks
  - `Staff`: **13** / 15 chunks

- **Số lượng Chunks cho phép đa vai trò (Multi-role Chunks)**: **15** chunks
- **Số lượng Chunks hạn chế quyền nhạy cảm (Restricted Chunks)**: **2** chunks (HR / Risk Management)
- **Độ ổn định định dạng `allowed_roles`**: **100% PARSE SUCCESS** (0 lỗi)

---

## 2. Kiểm thử Xử lý Vai trò Không hợp lệ (Unknown Role Handling)

- **Xử lý `UnknownRole`**: `Unknown roles: UnknownRole`
- **Nguyên tắc ngầm định (Default Deny)**: KHI TRUY VẤN VỚI VAI TRÒ KHÔNG HỢP LỆ, MÃ SẼ NẮM BẮT VÀ TỪ CHỐI TRUY CẬP (RAISE VALUEERROR).

---

## 3. Thử nghiệm Truy xuất Thực tế theo từng Vai trò (Single Query Benchmark)

**Query thử nghiệm**: *"Mức vốn điều lệ tối thiểu và quy định về kỷ luật lao động"*

| Vai trò người dùng (User Role) | Số chunks truy xuất được (BM25) | Đánh giá an toàn |
| :--- | :---: | :--- |
| `Admin` | **10** chunks | Quyền đầy đủ |
| `HR` | **5** chunks | Chỉ văn bản thuộc thẩm quyền |
| `Staff` | **10** chunks | Chỉ văn bản thuộc thẩm quyền |
| `Guest` | **3** chunks | Chỉ văn bản thuộc thẩm quyền |
| `Risk_Manager` (Không nằm trong system roles) | **0** (Từ chối truy cập) | Đảm bảo an toàn |
| `UnknownRole` | **0** (Báo lỗi tham số) | DEFAULT DENY PASS |

---

## 4. Tổng kết Kiểm định

1. **Tái sử dụng RBAC**: Đã tái sử dụng trực tiếp thuộc tính `allowed_roles` sẵn có từ Buổi 16 mà không cần sửa đổi dữ liệu hay thêm policy mới.
2. **Cơ chế Lọc trước Truy vấn (Filter Before Retrieval)**: Đã kiểm chứng `SecureRetriever` thực hiện lọc `_filter(user_roles)` trước khi thực hiện tìm kiếm.
3. **Tự động Từ chối Vai trò không hợp lệ**: Lỗi được bắt đúng và bảo mật mặc định từ chối.

---

RBAC REUSED: YES
FILTER BEFORE RETRIEVAL: PASS
UNKNOWN ROLE DEFAULT DENY: PASS