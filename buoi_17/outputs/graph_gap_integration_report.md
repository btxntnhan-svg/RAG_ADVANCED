# BÁO CÁO ĐÁNH GIÁ VAI TRÒ KNOWLEDGE GRAPH CHO COMPLIANCE GAP CHECKER

- **Ngày thực hiện**: 2026-08-25
- **Môi trường thực thi**: `buoi_17/`
- **Cơ sở dữ liệu Đồ thị**: Neo4j Graph DB (`bolt://localhost:7687`)
- **Nguyên tắc an toàn**: Không tự bịa edge hay mối quan hệ ảo trong Neo4j.

---

## 1. Kết quả Phân tích Schema & Relationship thực tế trong Neo4j

### 1.1. Thống kê các Nhãn Node (Node Labels)
- `(Document)`: **30** nodes
- `(CoQuan)`: **8** nodes
- `(NguoiKy)`: **13** nodes
- `(DoiTuongApDung)`: **5** nodes
- `(LinhVuc)`: **14** nodes
- `(VanBan)`: **15** nodes
- `(DieuKhoan)`: **15** nodes

### 1.2. Thống kê các Quan hệ (Relationship Types)
- `[:BAN_HANH_BOI]`: **30** edges
- `[:KY_BOI]`: **29** edges
- `[:AP_DUNG_CHO]`: **30** edges
- `[:THUOC_LINH_VUC]`: **19** edges
- `[:CONTAINS]`: **15** edges

---

## 2. Phân tích Chi tiết Vai trò từng Loại Quan hệ (Relationship Evaluation)

| Loại Quan hệ (Relationship Type) | Số lượng Edge | Mục đích & Phạm vi Liên kết | Đánh giá Giá trị cho Compliance Gap Checker |
| :--- | :---: | :--- | :--- |
| `[:CONTAINS]` | 15 | Liệt kê Điều khoản thuộc Văn bản (`VanBan` -> `DieuKhoan`) | **Chỉ mang tính cấu trúc hình học (Structural Hierarchy)**. Hỗ trợ tra cứu parent-child trong 1 văn bản, KHÔNG giúp nối văn bản nhà nước với quy định nội bộ. |
| `[:BAN_HANH_BOI]` | 30 | Liên kết Văn bản với Cơ quan ban hành (`Document` -> `CoQuan`) | **Siêu dữ liệu hành chính (Metadata Level)**. Không có giá trị trong việc so sánh nội dung hoặc gap tuân thủ. |
| `[:KY_BOI]` | 29 | Liên kết Văn bản với Người ký (`Document` -> `NguoiKy`) | **Siêu dữ liệu người ký (Metadata Level)**. Không liên quan tới đối soát gap tuân thủ. |
| `[:AP_DUNG_CHO]` | 30 | Liên kết Văn bản với Đối tượng áp dụng | **Siêu dữ liệu nhóm đối tượng (Broad Metadata)**. Quá tổng quát, không nối trực tiếp điều khoản cụ thể. |
| `[:THUOC_LINH_VUC]` | 19 | Liên kết Văn bản với Lĩnh vực quản lý | **Siêu dữ liệu phân loại (Category Metadata)**. Không chứa liên kết ngữ nghĩa cụ thể. |

---

## 3. Kết luận và Quyết định Tích hợp Đồ thị

1. **Bản chất của các quan hệ hiện tại**: Toàn bộ các relationship thực sự tồn tại trong Neo4j (`CONTAINS`, `BAN_HANH_BOI`, `KY_BOI`, `AP_DUNG_CHO`, `THUOC_LINH_VUC`) chỉ đóng vai trò phân cấp cấu trúc tệp tin và thuộc tính hành chính.
2. **Thiếu liên kết Ngữ nghĩa Liên miền (Missing Cross-Domain Semantic Edges)**: Đồ thị hiện chưa xây dựng các cạnh liên kết trực tiếp giữa Yêu cầu Tuân thủ Nhà nước (`EXTERNAL_REQUIREMENT`) và Điều khoản Quy định Nội bộ Ngân hàng (`INTERNAL_POLICY`).
3. **Quyết định Kỹ thuật**: **KHÔNG SỬ DỤNG GRAPH CHO KHÂU GAP MATCHING (GRAPH NOT USED FOR GAP MATCHING)**. Hệ thống giữ nguyên phương pháp **Hybrid Search (BM25 + Dense) kết hợp Cross-Encoder Reranker** làm engine tìm kiếm bằng chứng chính thức.

---

GRAPH USED: NO
REASON: Current Knowledge Graph relationships (CONTAINS, BAN_HANH_BOI, KY_BOI, AP_DUNG_CHO, THUOC_LINH_VUC) represent file hierarchy and administrative metadata only. Without explicit cross-domain compliance mapping edges between external regulations and internal policies, Hybrid Search + Cross-Encoder Reranker is the authoritative method for evidence retrieval.