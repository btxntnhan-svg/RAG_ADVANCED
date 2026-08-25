# BÁO CÁO RÀ SOÁT GAP TUÂN THỦ (COMPLIANCE GAP REPORT)

- **Ngày thực hiện**: 2026-08-25
- **Môi trường thực thi**: `buoi_17/`
- **Module**: `buoi_17/scripts/compliance_gap.py`
- **Kết quả Kiểm toán Dữ liệu (PROMPT 6)**: `COMPLIANCE GAP DATA: INSUFFICIENT`

---

## 1. Kết quả Đánh giá Dữ liệu cho Use Case Gap Analysis

> [!CAUTION]
> **BÁO CÁO THIẾU DỮ LIỆU VĂN BẢN NỘI BỘ (DATA GAP DISCOVERY)**:
> - Sử dụng nguyên tắc An toàn AI & Kiểm toán An ninh Thông tin của Buổi 17, hệ thống **không tự ý sinh văn bản giả lập hoặc gán nhãn sai lệch** một Thông tư/Luật nhà nước thành 'quy định nội bộ ngân hàng'.
> - Do tập corpus hiện tại chỉ chứa các **Văn bản Quy phạm Pháp luật của Nhà nước (`EXTERNAL_REQUIREMENT`)** và **THIẾU hoàn toàn Quy định Nội bộ (`INTERNAL_POLICY`)**, quy trình Rà soát Gap Tuân thủ tự động được tạm dừng để tránh sinh kết luận sai lệch (False Compliant / False Gap).

---

## 2. Schema Cấu trúc Kết quả Tuân thủ (Compliance Gap Schema)

Dưới đây là cấu trúc bảng dữ liệu `compliance_gap_results.csv` chuẩn hóa đã sẵn sàng để tiếp nhận dữ liệu khi bổ sung văn bản nội bộ:

| Trường dữ liệu (Field) | Mô tả chi tiết |
| :--- | :--- |
| `gap_id` | Mã định danh duy nhất cho vấn đề gap tuân thủ (ví dụ: `GAP_001`) |
| `external_document_id` | Mã định danh văn bản nhà nước (NHNN/Chính phủ) |
| `external_chunk_id` | Mã chunk yêu cầu nhà nước |
| `external_requirement` | Nội dung yêu cầu tuân thủ nhà nước |
| `external_citation` | Trích dẫn điều khoản nhà nước |
| `internal_document_id` | Mã định danh văn bản quy định nội bộ ngân hàng |
| `internal_chunk_id` | Mã chunk bằng chứng nội bộ |
| `internal_evidence` | Nội dung bằng chứng nội bộ |
| `internal_citation` | Trích dẫn điều khoản nội bộ |
| `classification` | Phân loại tuân thủ: `DAP_UNG` / `THIEU` / `CHENH_LECH` / `CHUA_DU_BANG_CHUNG` |
| `reason` | Giải thích ngắn gọn căn cứ phân loại |
| `confidence` | Độ tin cậy đánh giá (0.0 - 1.0) |
| `review_status` | Trạng thái phê duyệt: `NEEDS_HUMAN_REVIEW` |
| `request_id` | Mã yêu cầu truy vết Audit Log |

---

## 3. Khuyến nghị Bổ sung Dữ liệu

1. **Bổ sung Corpus Văn bản Nội bộ**: Nạp thêm các văn bản Quy chế Quản lý Kho tiền, Quy định An toàn Vốn nội bộ, Nội quy Lao động của Ngân hàng Thương mại vào dataset.
2. **Thực thi Chuyên gia Kiểm duyệt (Human-in-the-Loop)**: Mọi kết quả phân loại tuân thủ AI sinh ra bắt buộc phải có trạng thái `review_status = NEEDS_HUMAN_REVIEW` để Cán bộ Tuân thủ (Compliance Officer) phê duyệt.

---

GAP CHECKER: PASS
HUMAN REVIEW REQUIRED: YES