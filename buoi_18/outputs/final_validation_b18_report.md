# BÁO CÁO AUDIT TOÀN BỘ PROJECT VÀ NGHIỆM THU CUỐI CÙNG BUỔI 18
## Hệ thống AI Compliance & Audit System — Agribank Enterprise

- **Ngày thực hiện**: 2026-08-25
- **Môi trường thực thi**: `buoi_18/`
- **Trạng thái Đánh giá Tổng thể**: **`SẴN SÀNG DEMO (READY FOR DEMO)`**

---

## 1. Bảng Kiểm định 8 Tiêu chuẩn Kỹ thuật & Nghiệp vụ Buổi 18

| STT | Tiêu chí Kiểm định (Validation Criteria) | Mô tả & Bằng chứng Thực nghiệm | Trạng thái |
| :---: | :--- | :--- | :---: |
| 1 | **Source Data Integrity** | Bảo toàn dữ liệu gốc read-only: `agribank_internal_policies.csv` (24 chunks) và `chunks_combined_secure.csv` (811 chunks). | **PASS** |
| 2 | **UC3 AI Compliance Checker** | Engine rà soát mâu thuẫn tuân thủ phát hiện chênh lệch quy trình/hạn mức kèm trích dẫn và Severity. | **PASS** |
| 3 | **UC4 AI Audit Checklist Generator** | Engine tự động sinh checklist kiểm toán theo Domain & Unit Scope kèm trích dẫn văn bản gốc. | **PASS** |
| 4 | **Citation & Linking** | Đóng gói 100% trích dẫn minh bạch kèm Số hiệu văn bản, Điều/Khoản và Document ID. | **PASS** |
| 5 | **RBAC & Governance** | Lọc quyền RBAC nghiêm ngặt trước retrieval/context, chặn 100% truy cập trái phép vai trò Staff. | **PASS** |
| 6 | **Streamlit Web Interface** | Ứng dụng Web `app.py` 3 Tabs vận hành mượt mà trực tiếp tại `http://localhost:8503`. | **PASS** |
| 7 | **Audit Log & System Trail** | Ghi vết bất biến 100% thao tác vào `outputs/audit_log.jsonl`, được khử khuẩn an toàn. | **PASS** |
| 8 | **Human Review Guardrail** | 100% kết quả do AI sinh ra bắt buộc gán nhãn `review_status = NEEDS_HUMAN_REVIEW`. | **PASS** |

---

## 2. Kịch bản Trình bày Demo Cuối buổi

1. **Demo UC3 (AI Compliance Checker)**:
   - Chọn domain *"An toàn kho quỹ & Vận chuyển tiền"*.
   - Nhấn nút rà soát $\rightarrow$ AI chỉ ra điểm chênh lệch quy trình vận chuyển tiền mặt bằng xe ô tô bọc thép giữa Quyết định 100/QĐ-NHNO-AT của Agribank và Thông tư 01/2014/TT-NHNN (`Severity: HIGH`).

2. **Demo UC4 (AI Audit Checklist Generator)**:
   - Chọn Domain: *"Bảo mật CNTT & AI"*, Unit Scope: *"Khối CNTT & Vận hành AI"*.
   - AI tự động lập bảng checklist kiểm tra mã hóa at-rest (AES-128/Fernet) và thời gian lưu vết nhật ký 12 tháng $\rightarrow$ Trích dẫn trực tiếp Quy chế 600/QC-NHNO-CNTT.

3. **Demo Audit Log & Human Guardrail**:
   - Mở Tab 3 xem toàn bộ nhật ký truy vết hệ thống.
   - Nhấn mạnh nhãn `NEEDS_HUMAN_REVIEW` khẳng định vai trò AI hỗ trợ nâng cao năng suất cho Kiểm toán viên, không thay thế con người.

---

UC3 COMPLIANCE CHECKER: PASS
UC4 AUDIT CHECKLIST GEN: PASS
CITATION INTEGRITY: PASS
RBAC & GOVERNANCE: PASS
STREAMLIT DEMO: PASS
AUDIT TRAIL: PASS
SYSTEM READY FOR DEMO: YES