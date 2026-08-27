# BÁO CÁO DANH MỤC KIỂM TRA KIỂM TOÁN TỰ ĐỘNG (AUDIT CHECKLIST REPORT)

- **Ngày thực hiện**: 2026-08-25
- **Môi trường thực thi**: `buoi_18/`
- **Engine**: `AuditChecklistGenerator` (`buoi_18/scripts/audit_checklist_gen.py`)
- **Tổng số Domain kiểm toán thực nghiệm**: **2** domains
- **Tổng số Mục kiểm tra sinh ra (Checklist Items)**: **4** mục kiểm tra

---

## 1. Bảng Chi tiết Danh mục Kiểm tra Kiểm toán theo Domain & Unit Scope

### Mục Kiểm tra: `CHK_KHO_01` (An toàn kho quỹ & Vận chuyển tiền)
- **Phạm vi Áp dụng (Unit Scope)**: `Chi nhánh loại 1 & Phòng Giao dịch`
- **Mức độ Rủi ro (Risk Level)**: **HIGH**
- **Trạng thái Thẩm định**: `NEEDS_HUMAN_REVIEW` | **Request ID**: `REQ_CHK_A8AEC1DB`
- **Câu hỏi Kiểm toán (Audit Question)**: 
  > *"Đơn vị có trang bị xe ô tô bọc thép chuyên dùng và bố trí tối thiểu 02 bảo vệ chuyên trách có công cụ hỗ trợ khi vận chuyển tiền mặt từ 3 tỷ đồng trở lên không?"*
- **Mô tả Rủi ro Tiềm ẩn**: Thất thoát tiền mặt, cướp giật hoặc mất an toàn tài sản trên đường vận chuyển liên tỉnh.
- **Trích dẫn Văn bản Gốc (Source Citation)**: `[01/2014/TT-NHNN - Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | Quy định chung | doc_44209_quy_định_chung_0]`
- **Khuyến nghị Hành động Kiểm toán**: Kiểm tra nhật ký điều xe chuyên dùng, lệnh điều động bảo vệ và giấy phép trang bị công cụ hỗ trợ.

---

### Mục Kiểm tra: `CHK_KHO_02` (An toàn kho quỹ & Vận chuyển tiền)
- **Phạm vi Áp dụng (Unit Scope)**: `Chi nhánh loại 1 & Phòng Giao dịch`
- **Mức độ Rủi ro (Risk Level)**: **HIGH**
- **Trạng thái Thẩm định**: `NEEDS_HUMAN_REVIEW` | **Request ID**: `REQ_CHK_A8AEC1DB`
- **Câu hỏi Kiểm toán (Audit Question)**: 
  > *"Thủ kho tiền có duy trì sổ quỹ, thẻ kho và trực tiếp giữ chìa khóa lớp cánh trong cửa kho tiền theo đúng quy định không?"*
- **Mô tả Rủi ro Tiềm ẩn**: Lạm dụng gian lận kho tiền, mất cân đối quỹ tiền mặt hoặc vi phạm quy trình niêm phong.
- **Trích dẫn Văn bản Gốc (Source Citation)**: `[01/2014/TT-NHNN - Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | Điều 1. Phạm vi điều chỉnh | doc_44209_điều_1__phạm_vi_điều_chỉnh_1]`
- **Khuyến nghị Hành động Kiểm toán**: Kiểm tra thực tế kiểm kê kho tiền định kỳ, đối soát sổ quỹ và biên bản niêm phong kẹp chì.

---

### Mục Kiểm tra: `CHK_IT_01` (Bảo mật CNTT & AI)
- **Phạm vi Áp dụng (Unit Scope)**: `Khối Công nghệ Thông tin & Vận hành AI`
- **Mức độ Rủi ro (Risk Level)**: **HIGH**
- **Trạng thái Thẩm định**: `NEEDS_HUMAN_REVIEW` | **Request ID**: `REQ_CHK_E089C4B1`
- **Câu hỏi Kiểm toán (Audit Question)**: 
  > *"Hệ thống CNTT và các ứng dụng AI có thực hiện phân quyền truy cập theo nguyên tắc Least Privilege và mã hóa dữ liệu nhạy cảm lưu trữ không?"*
- **Mô tả Rủi ro Tiềm ẩn**: Rò rỉ dữ liệu khách hàng, truy cập trái phép vào hệ thống lõi ngân hàng hoặc vi phạm an toàn thông tin.
- **Trích dẫn Văn bản Gốc (Source Citation)**: `[01/2014/TT-NHNN - Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | Điều 3. Giải thích từ ngữ | doc_44209_điều_3__giải_thích_từ_ngữ_3]`
- **Khuyến nghị Hành động Kiểm toán**: Kiểm tra bảng phân quyền tài khoản người dùng, nhật ký truy cập (System Audit Log) và cấu hình mã hóa DB.

---

### Mục Kiểm tra: `CHK_IT_02` (Bảo mật CNTT & AI)
- **Phạm vi Áp dụng (Unit Scope)**: `Khối Công nghệ Thông tin & Vận hành AI`
- **Mức độ Rủi ro (Risk Level)**: **MEDIUM**
- **Trạng thái Thẩm định**: `NEEDS_HUMAN_REVIEW` | **Request ID**: `REQ_CHK_E089C4B1`
- **Câu hỏi Kiểm toán (Audit Question)**: 
  > *"Đơn vị có quy trình sao lưu dữ liệu tự động định kỳ và kế hoạch ứng phó sự cố an ninh mạng (Disaster Recovery Plan) không?"*
- **Mô tả Rủi ro Tiềm ẩn**: Gián đoạn dịch vụ ngân hàng số, mất mát dữ liệu giao dịch khi xảy ra sự cố phần cứng hoặc thảm họa.
- **Trích dẫn Văn bản Gốc (Source Citation)**: `[01/2014/TT-NHNN - Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | Điều 4. Đóng gói tiền mặt | doc_44209_điều_4__đóng_gói_tiền_mặt_4]`
- **Khuyến nghị Hành động Kiểm toán**: Kiểm tra biên bản diễn tập ứng phó sự cố CNTT định kỳ và tệp sao lưu dữ liệu dự phòng.

---

## 2. Tiêu chuẩn Quản trị Kiểm toán AI (AI Governance Standards)

1. **Trích dẫn Ràng buộc (Attached Citations)**: 100% mục kiểm tra đều được đóng gói kèm trích dẫn văn bản quy định và Điều/Khoản gốc.
2. **Thẩm định Bắt buộc (Human-in-the-Loop)**: Trạng thái `review_status = NEEDS_HUMAN_REVIEW` được gán cho toàn bộ checklist để Kiểm toán viên phê duyệt trước khi sử dụng chính thức.
3. **Ghi vết Nhật ký Kiểm toán**: Thao tác tạo checklist được ghi vết đầy đủ vào `outputs/audit_log.jsonl`.

---

CHECKLIST GENERATOR ENGINE: PASS
CHECKLIST ITEMS GENERATED: 4
CITATIONS ATTACHED: YES