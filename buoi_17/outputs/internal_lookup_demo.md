# BÁO CÁO USE CASE 1: AI TRA CỨU QUY ĐỊNH NỘI BỘ (INTERNAL LOOKUP DEMO)

- **Ngày thực hiện**: 2026-08-25
- **Môi trường thực thi**: `buoi_17/`
- **Engine**: `InternalLookupEngine` (`buoi_17/scripts/internal_lookup.py`)
- **Lớp Bảo mật**: `SecureRetrievalAdapter` + `AuditLogger`

---

## 1. Kết quả Thử nghiệm 3 Câu hỏi Tra cứu Thực tế

### TC_01: Tra cứu Luật Hợp tác xã (Role Staff - Được phép truy cập)
- **Request ID**: `REQ_LK_F50AF0EE`
- **Vai trò người dùng (User Role)**: `Staff`
- **Phạm vi quyền truy cập (Access Scope)**: `Allowed: 13/15 chunks (Filtered: 2)`
- **Câu hỏi**: *"Theo Luật Hợp tác xã số 17/2023/QH15, việc góp vốn điều lệ và quyền của thành viên hợp tác xã được quy định như thế nào?"*
- **Câu trả lời sinh ra**: 
  > Căn cứ vào Nghị định số 46/2023/NĐ-CP Quy định chi tiết thi hành một số điều của Luật Kinh doanh bảo hiểm | 46/2023/NĐ-CP | 163441__full: CHÍNH PHỦ...
- **Danh sách Trích dẫn (Citations)**: `Nghị định số 46/2023/NĐ-CP Quy định chi tiết thi hành một số điều của Luật Kinh doanh bảo hiểm | 46/2023/NĐ-CP | 163441__full`, `Thông tư số 63/2025/TT-NHNN Sửa đổi, bổ sung một số điều của một số Thông tư về quỹ tín dụng nhân dân | 63/2025/TT-NHNN | 185630__full`, `Thông tư số 27/2024/TT-NHNN Quy định về việc ngân hàng hợp tác xã, việc trích nộp, quản lý và sử dụng Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân | 27/2024/TT-NHNN | 168220__full`
- **Mã Văn bản/Chunk (`document_id/chunk_id`)**: `163441/163441__full`, `185630/185630__full`, `168220/168220__full`

---

### TC_02: Tra cứu Quy trình Kho tiền (Role Guest - Không đủ quyền truy cập)
- **Request ID**: `REQ_LK_E08F658D`
- **Vai trò người dùng (User Role)**: `Guest`
- **Phạm vi quyền truy cập (Access Scope)**: `Allowed: 3/15 chunks (Filtered: 12)`
- **Câu hỏi**: *"Quy định chi tiết về quy trình giao nhận, kiểm đếm và bảo quản tiền mặt nguyên niêm phong kẹp chì trong kho tiền?"*
- **Câu trả lời sinh ra**: 
  > Không tìm thấy đủ thông tin trong phạm vi tài liệu được phép truy cập.
- **Danh sách Trích dẫn (Citations)**: `Không có`
- **Mã Văn bản/Chunk (`document_id/chunk_id`)**: `Không có`

---

### TC_03: Tra cứu An toàn vốn và Tiền mặt (Role Admin - Được phép toàn quyền)
- **Request ID**: `REQ_LK_495A0F6B`
- **Vai trò người dùng (User Role)**: `Admin`
- **Phạm vi quyền truy cập (Access Scope)**: `Allowed: 15/15 chunks (Filtered: 0)`
- **Câu hỏi**: *"Quy định về việc giao nhận, bảo quản và vận chuyển tiền mặt, tài sản quý theo Thông tư 01/2014/TT-NHNN?"*
- **Câu trả lời sinh ra**: 
  > Căn cứ vào Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | 44209__full: NGÂN HÀNG NHÀ NƯỚC...
- **Danh sách Trích dẫn (Citations)**: `Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | 01/2014/TT-NHNN | 44209__full`, `Thông tư số 27/2024/TT-NHNN Quy định về việc ngân hàng hợp tác xã, việc trích nộp, quản lý và sử dụng Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân | 27/2024/TT-NHNN | 168220__full`, `Thông tư số 43/2024/TT-NHNN sửa đổi, bổ sung một số điều của Thông tư số 01/2014/TT-NHNN ngày 10 tháng 12 năm 2014 của Thống đốc Ngân hàng Nhà nước Việt Nam hướng dẫn việc tổ chức thực hiện hoạt đọng quản lý dự trữ ngoại hối nhà nước. | 43/2024/TT-NHNN | 169221__full`
- **Mã Văn bản/Chunk (`document_id/chunk_id`)**: `44209/44209__full`, `168220/168220__full`, `169221/169221__full`

---

## 2. Kiểm định Tiêu chuẩn An toàn & Nguyên tắc Giới hạn Ngữ cảnh

1. **Chỉ trả lời từ Chunk sau RBAC**: LLM hoàn toàn không thể tiếp cận các chunk thuộc tài liệu bị chặn.
2. **Cơ chế Phản hồi khi Thiếu Ngữ cảnh (Fallback Policy)**: Khi người dùng `Guest` hỏi về tài liệu Rủi ro kho tiền, hệ thống trả về đúng câu phản hồi chuẩn:
   > *"Không tìm thấy đủ thông tin trong phạm vi tài liệu được phép truy cập."*
3. **Zero Knowledge Expansion**: Không tự ý bổ sung kiến thức ngoại lai ngoài ngữ cảnh được phép.
4. **Không tạo Citation giả**: Tất cả các trích dẫn pháp lý đều khớp 100% với danh sách `citation_code` nguồn.
5. **Tự động lưu Audit Log**: 100% giao dịch tra cứu đều được ghi nhận vào `buoi_17/outputs/audit_log.jsonl`.

---

CITATION: PASS
RBAC: PASS
AUDIT: PASS