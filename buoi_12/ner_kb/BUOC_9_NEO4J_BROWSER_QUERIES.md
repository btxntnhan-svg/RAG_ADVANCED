# BƯỚC 9 — Kiểm tra Knowledge Graph trên Neo4j Browser

Sau khi chạy `ner_kb_pipeline.py`, sử dụng các query dưới đây trên **Neo4j Browser** (mở tại `http://localhost:7474`).

---

## 9.1. Kiểm tra số Node theo Label

```cypher
MATCH (n)
RETURN labels(n) AS labels, count(*) AS total
ORDER BY total DESC;
```

**Kỳ vọng:**
- Document: 30
- LinhVuc: 14
- NguoiKy: 13
- CoQuan: 8
- DoiTuongApDung: 5
- **Tổng: 70 node**

---

## 9.2. Kiểm tra số Relationship theo Type

```cypher
MATCH ()-[r]->()
RETURN type(r) AS relationship_type, count(*) AS total
ORDER BY total DESC;
```

**Kỳ vọng:**
- BAN_HANH_BOI: 30
- AP_DUNG_CHO: 30
- KY_BOI: 29
- THUOC_LINH_VUC: 19
- **Tổng: 108 relationship**

---

## 9.3. Văn bản và Người ký

Xem mối liên hệ giữa Văn bản và người ký nó.

```cypher
MATCH (d:Document)-[:KY_BOI]->(p:NguoiKy)
RETURN d.id AS doc_id, d.so_ky_hieu AS so_ky_hieu, p.name AS signer
LIMIT 20;
```

**Mô tả:**
- Mỗi dòng hiển thị: ID văn bản → Người ký
- Ví dụ: `112025 | 73/2016/NĐ-CP | Nguyễn Xuân Phúc`

---

## 9.4. Văn bản và Đối tượng áp dụng

Xem đối tượng chịu sự điều chỉnh của từng văn bản.

```cypher
MATCH (d:Document)-[:AP_DUNG_CHO]->(o:DoiTuongApDung)
RETURN d.id AS doc_id, d.so_ky_hieu AS so_ky_hieu, o.name AS target
LIMIT 20;
```

**Mô tả:**
- Ví dụ: `112025 | 73/2016/NĐ-CP | Trung ương`

---

## 9.5. Văn bản và Cơ quan ban hành

Xem cơ quan nào ban hành từng văn bản.

```cypher
MATCH (d:Document)-[:BAN_HANH_BOI]->(c:CoQuan)
RETURN d.id AS doc_id, d.so_ky_hieu AS so_ky_hieu, c.name AS issuing_agency
LIMIT 20;
```

**Mô tả:**
- Ví dụ: `112025 | 73/2016/NĐ-CP | Chính phủ`

---

## 9.6. Văn bản thuộc Lĩnh vực

Xem văn bản thuộc lĩnh vực pháp lý nào.

```cypher
MATCH (d:Document)-[:THUOC_LINH_VUC]->(l:LinhVuc)
RETURN d.id AS doc_id, d.so_ky_hieu AS so_ky_hieu, l.name AS linh_vuc
LIMIT 20;
```

**Mô tả:**
- Ví dụ: `146468 | 10/2024/QH15 | Chứng khoán`
- Không phải mọi văn bản đều có lĩnh vực (một số để trống).

---

## 9.7. Visualize Graph — All Relationships

Xem toàn bộ cấu trúc graph (hạn chế để tránh quá tải browser).

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 100;
```

**Ghi chú:**
- Nhấp vào nút để xem chi tiết.
- Màu sắc tự động phân loại theo label.

---

## 9.8. Liệt kê tất cả Document

Xem danh sách 30 văn bản đã import.

```cypher
MATCH (d:Document)
RETURN d.id AS doc_id, d.so_ky_hieu AS so_ky_hieu
ORDER BY d.id
LIMIT 50;
```

**Mô tả:**
- Liệt kê tất cả document có trong database.

---

## 9.9. Liệt kê tất cả Entity

Xem danh sách các cơ quan, người ký, đối tượng áp dụng, lĩnh vực.

```cypher
MATCH (n:CoQuan|NguoiKy|DoiTuongApDung|LinhVuc)
RETURN labels(n) AS entity_type, n.name AS name, count(*) AS frequency
GROUP BY entity_type, n.name
ORDER BY frequency DESC
LIMIT 50;
```

**Mô tả:**
- Hiển thị mọi entity và tần suất xuất hiện.
- Giúp kiểm tra normalization có đúng không.

---

## 9.10. Kiểm tra Relationship Type

Xem chi tiết tất cả relationship types.

```cypher
MATCH ()-[r]->()
RETURN type(r) AS rel_type, count(*) AS count
ORDER BY count DESC;
```

**Kỳ vọng (tương tự 9.2):**
- BAN_HANH_BOI: 30
- AP_DUNG_CHO: 30
- KY_BOI: 29
- THUOC_LINH_VUC: 19

---

## 9.11. Kiểm tra từng Cơ quan

Xem cơ quan nào ban hành bao nhiêu văn bản.

```cypher
MATCH (d:Document)-[:BAN_HANH_BOI]->(c:CoQuan)
RETURN c.name AS agency, count(d) AS num_documents
ORDER BY num_documents DESC;
```

**Mô tả:**
- Ví dụ: Chính phủ ban hành 15 văn bản, Bộ Tài chính ban hành 8 văn bản...

---

## 9.12. Kiểm tra từng Người ký

Xem người nào ký bao nhiêu văn bản.

```cypher
MATCH (d:Document)-[:KY_BOI]->(p:NguoiKy)
RETURN p.name AS signer, count(d) AS num_documents
ORDER BY num_documents DESC;
```

**Mô tả:**
- Ví dụ: Nguyễn Xuân Phúc ký 5 văn bản, Trần Xuân Hà ký 3 văn bản...

---

## 9.13. Kiểm tra Lĩnh vực

Xem mỗi lĩnh vực có bao nhiêu văn bản.

```cypher
MATCH (d:Document)-[:THUOC_LINH_VUC]->(l:LinhVuc)
RETURN l.name AS field, count(d) AS num_documents
ORDER BY num_documents DESC;
```

---

## 9.14. Đối tượng áp dụng

Xem mỗi đối tượng bị sự điều chỉnh bao nhiêu văn bản.

```cypher
MATCH (d:Document)-[:AP_DUNG_CHO]->(o:DoiTuongApDung)
RETURN o.name AS target_object, count(d) AS num_documents
ORDER BY num_documents DESC;
```

**Kỳ vọng:**
- Phần lớn là "Trung ương".

---

## 9.15. Tìm kiếm Document theo ID

Xem toàn bộ thông tin một văn bản cụ thể.

```cypher
MATCH (d:Document {id: '112025'})
RETURN d;
```

**Ghi chú:** Thay `'112025'` bằng ID bất kỳ từ danh sách (Bước 9.8).

---

## 9.16. Tìm kiếm Document theo So ký hiệu

```cypher
MATCH (d:Document {so_ky_hieu: '73/2016/NĐ-CP'})
RETURN d;
```

---

## 9.17. Tìm tất cả Entity liên kết với một Document

Xem tất cả cơ quan, người ký, đối tượng, lĩnh vực của một văn bản.

```cypher
MATCH (d:Document {id: '112025'})-[r]->(n)
RETURN type(r) AS relationship, labels(n) AS entity_type, n.name AS name;
```

---

## Hướng dẫn sử dụng Neo4j Browser

1. **Mở browser:** http://localhost:7474
2. **Đăng nhập:** 
   - Username: `neo4j`
   - Password: `password` (hoặc theo `.env`)
3. **Dán query:** Vào ô `:` ở phía trên.
4. **Chạy:** Nhấn `Ctrl+Enter` hoặc nút play.
5. **Xem kết quả:**
   - **Table:** Dữ liệu dạng bảng.
   - **Graph:** Trực quan quan hệ (đặc biệt hữu ích cho MATCH pattern).

---

## Checklist cuối cùng

- [ ] Node count = 70 (Bước 9.1)
- [ ] Relationship count = 108 (Bước 9.2)
- [ ] Document-NguoiKy có kết quả (Bước 9.3)
- [ ] Document-DoiTuongApDung có kết quả (Bước 9.4)
- [ ] Document-CoQuan có kết quả (Bước 9.5)
- [ ] Document-LinhVuc có kết quả (Bước 9.6)
- [ ] Graph có thể visualize được (Bước 9.7)
- [ ] 30 Document được import (Bước 9.8)
- [ ] Entity không bị duplicate (Bước 9.9)

---

## Nếu có lỗi

**Q: Relationship type `THAM_CHIEU` không tồn tại?**
- A: Bình thường. Document→Document relationship bị lọc trong validation vì target không nằm trong corpus. Graph đã được validate trước khi import.

**Q: Một số Document không có entity liên kết?**
- A: Bình thường. Metadata gốc có thể không đầy đủ; các Document được import nhưng không phải mọi liên kết đều tồn tại.

**Q: Làm sao sửa database?**
- A: Không sửa trực tiếp. Nếu cần thay đổi logic:
  1. Sửa `ner_kb_pipeline.py`
  2. Xóa toàn bộ node/relationship cũ (hoặc tạo database mới)
  3. Chạy lại pipeline

---

## Tài liệu thêm

- Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual/current/
- Neo4j Browser Intro: https://neo4j.com/docs/browser-manual/current/
