# BÁO CÁO KẾT QUẢ RÀ SOÁT MÂU THUẪN TUÂN THỦ (COMPLIANCE CONFLICT REPORT)

- **Ngày thực hiện**: 2026-08-25
- **Môi trường thực thi**: `buoi_18/`
- **Engine**: `ComplianceCheckerEngine` (`buoi_18/scripts/compliance_checker.py`)
- **Tổng số cặp văn bản đã đối soát**: **3** cặp văn bản
- **Số lượng Mâu thuẫn / Chênh lệch phát hiện**: **3** xung đột

---

## 1. Chi tiết Bảng Kết quả Rà soát Mâu thuẫn Tuân thủ

### Mã Mâu thuẫn: `CONF_07CB70` (An toàn Kho quỹ & Vận chuyển Tiền mặt)
- **Request ID**: `REQ_CONF_4EF79BBF`
- **Loại Xung đột (Conflict Type)**: `Thời hạn hiệu lực`
- **Mức độ Nghiêm trọng (Severity)**: **LOW**
- **Trạng thái Thẩm định (Review Status)**: `NEEDS_HUMAN_REVIEW`
- **Văn bản A (Nội bộ Agribank)**: `[100/QĐ-NHNO-AT - Quy định nội bộ số 100/QĐ-NHNO-AT | Điều 1 | doc_agr_at01_01]`
  > *Evidence A*: Quy định này áp dụng đối với toàn bộ cán bộ công nhân viên thuộc chi nhánh, phòng giao dịch Agribank trong công tác giao nhận, kiểm đếm, bảo quản và vận chuyển tiền mặt, tài sản qu...
- **Văn bản B (Pháp luật Nhà nước / Tham chiếu)**: `[01/2014/TT-NHNN - Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá | Quy định chung | doc_44209_quy_định_chung_0]`
  > *Evidence B*: Văn bản: Thông tư số 01/2014/TT-NHNN Quy định về giao nhận, bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá (Số ký hiệu: 01/2014/TT-NHNN) Quy định chung NGÂN HÀNG NHÀ NƯ...
- **Mô tả Mâu thuẫn Chi tiết**: Phát hiện khác biệt về mốc thời gian áp dụng giữa 100/QĐ-NHNO-AT và 01/2014/TT-NHNN.

---

### Mã Mâu thuẫn: `CONF_2DE85A` (CAR & Quản lý Rủi ro)
- **Request ID**: `REQ_CONF_39C772D4`
- **Loại Xung đột (Conflict Type)**: `Hạn mức/Ngưỡng`
- **Mức độ Nghiêm trọng (Severity)**: **HIGH**
- **Trạng thái Thẩm định (Review Status)**: `NEEDS_HUMAN_REVIEW`
- **Văn bản A (Nội bộ Agribank)**: `[250/QĐ-NHNO-QLRR - Quy định nội bộ số 250/QĐ-NHNO-QLRR | Điều 5 | doc_agr_car02_01]`
  > *Evidence A*: Tỷ lệ an toàn vốn tối thiểu (CAR) của Agribank được quy định duy trì ở mức tối thiểu 8.5%, cao hơn 0.5% so với quy định chung 8% tại Thông tư 41/2016/TT-NHNN. Bộ phận Quản lý Rủi r...
- **Văn bản B (Pháp luật Nhà nước / Tham chiếu)**: `[41/2016/TT-NHNN - Thông tư số 41/2016/TT-NHNN Quy định tỷ lệ an toàn vốn đối với ngân hàng, chi nhánh ngân hàng nước ngoài | Quy định chung | doc_117310_quy_định_chung_0]`
  > *Evidence B*: Văn bản: Thông tư số 41/2016/TT-NHNN Quy định tỷ lệ an toàn vốn đối với ngân hàng, chi nhánh ngân hàng nước ngoài (Số ký hiệu: 41/2016/TT-NHNN) Quy định chung THÔNG TƯ Quy định tỷ ...
- **Mô tả Mâu thuẫn Chi tiết**: Phát hiện chênh lệch ngưỡng an toàn vốn tối thiểu (CAR) giữa Quy định quản lý rủi ro Agribank (250/QĐ-NHNO-QLRR) và Thông tư 41/2016/TT-NHNN (41/2016/TT-NHNN). Cần đối soát lại tỷ lệ đệm vốn rủi ro hoạt động.

---

### Mã Mâu thuẫn: `CONF_993558` (Tín dụng & Phân cấp Phê duyệt)
- **Request ID**: `REQ_CONF_61833084`
- **Loại Xung đột (Conflict Type)**: `Thẩm quyền phê duyệt`
- **Mức độ Nghiêm trọng (Severity)**: **MEDIUM**
- **Trạng thái Thẩm định (Review Status)**: `NEEDS_HUMAN_REVIEW`
- **Văn bản A (Nội bộ Agribank)**: `[315/QC-NHNO-TD - Quy chế tín dụng nội bộ số 315/QC-NHNO-TD | Điều 8 | doc_agr_td03_01]`
  > *Evidence A*: Thẩm quyền phán quyết tín dụng của Giám đốc Chi nhánh Agribank loại I là tối đa 30 tỷ đồng đối với khách hàng doanh nghiệp và 10 tỷ đồng đối với khách hàng cá nhân. Các khoản vay v...
- **Văn bản B (Pháp luật Nhà nước / Tham chiếu)**: `[27/2024/TT-NHNN - Thông tư số 27/2024/TT-NHNN Quy định về việc ngân hàng hợp tác xã, việc trích nộp, quản lý và sử dụng Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân | Quy định chung | doc_168220_quy_định_chung_0]`
  > *Evidence B*: Văn bản: Thông tư số 27/2024/TT-NHNN Quy định về việc ngân hàng hợp tác xã, việc trích nộp, quản lý và sử dụng Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân (Số ký hiệu: 27/20...
- **Mô tả Mâu thuẫn Chi tiết**: Phát hiện điểm chưa đồng bộ về hạn mức phán quyết ủy quyền cho vay tín dụng Agribank (315/QC-NHNO-TD) với quy định cấp phép TCTD (27/2024/TT-NHNN).

---

## 2. Tiêu chuẩn Thẩm định Cán bộ Tuân thủ (Human Review Guardrail)

> [!IMPORTANT]
> **NGUYÊN TẮC BẢO MẬT & QUẢN TRỊ AI (HUMAN-IN-THE-LOOP MANDATE)**:
> 1. **100% Cờ Thẩm định**: Toàn bộ kết quả xung đột tuân thủ do AI sinh ra bắt buộc gán trạng thái `review_status = NEEDS_HUMAN_REVIEW`.
> 2. **Trích dẫn Minh bạch**: Bắt buộc sử dụng 100% Citation pháp lý & nội bộ có thực từ dataset nguồn, không bịa đặt điều khoản.
> 3. **Nhật ký Truy vết Bất biến**: Mọi thao tác đối soát đều được ghi vết tự động vào `outputs/audit_log.jsonl`.

---

COMPLIANCE CHECKER ENGINE: PASS
CONFLICTS DETECTED: 3
HUMAN REVIEW GUARDRAIL: PASS