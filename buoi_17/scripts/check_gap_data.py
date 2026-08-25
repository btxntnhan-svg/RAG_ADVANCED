"""Script auditing corpus documents for Compliance Gap Analysis for Buoi 17."""

from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent

def determine_issuer_and_type(row: pd.Series) -> tuple[str, str, str, str]:
    title = str(row.get("title", ""))
    doc_type = str(row.get("document_type", ""))
    citation = str(row.get("citation_code", ""))
    source_file = str(row.get("source_file", ""))

    # Classify based on authentic legal evidence
    if "NHNN" in citation or "NHNN" in title or "Ngân hàng Nhà nước" in title:
        issuer = "Ngân hàng Nhà nước Việt Nam"
        classification = "EXTERNAL_REQUIREMENT"
        evidence = "Cơ quan ban hành: Ngân hàng Nhà nước Việt Nam (Thông tư/VBHN quy phạm pháp luật ngành ngân hàng)"
    elif "QH" in citation or "QH" in title or "Luật" in title:
        issuer = "Quốc hội"
        classification = "EXTERNAL_REQUIREMENT"
        evidence = "Cơ quan ban hành: Quốc hội nước SRVN (Luật quy phạm pháp luật cấp cao)"
    elif "NĐ-CP" in citation or "NĐ-CP" in title or "Nghị định" in title:
        issuer = "Chính phủ"
        classification = "EXTERNAL_REQUIREMENT"
        evidence = "Cơ quan ban hành: Chính phủ (Nghị định quy định chi tiết thi hành Luật)"
    elif "TT-BTC" in citation or "BTC" in title:
        issuer = "Bộ Tài chính"
        classification = "EXTERNAL_REQUIREMENT"
        evidence = "Cơ quan ban hành: Bộ Tài chính (Thông tư hướng dẫn quản lý tài chính/đầu tư)"
    else:
        # Check internal policy evidence
        if "QĐ-NH" in citation or "Quy định nội bộ" in title or "Quy trình nội bộ" in title:
            issuer = "Ngân hàng Thương mại (Nội bộ)"
            classification = "INTERNAL_POLICY"
            evidence = "Văn bản quy định/quy trình vận hành nội bộ của ngân hàng"
        else:
            issuer = "Cơ quan Nhà nước"
            classification = "EXTERNAL_REQUIREMENT"
            evidence = "Văn bản quy phạm pháp luật nhà nước"

    return issuer, doc_type or "Thông tư/Nghị định/Luật", classification, evidence


def main() -> None:
    csv_path = WORKSPACE_ROOT / "buoi_16" / "data" / "processed" / "chunks_secure.csv"
    if not csv_path.exists():
        csv_path = WORKSPACE_ROOT / "buoi_14" / "data" / "processed" / "chunks_secure.csv"

    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)

    # Group by document_id
    grouped = df.groupby("document_id")
    total_docs = len(grouped)

    doc_catalog = []
    internal_count = 0
    external_count = 0

    for doc_id, group in grouped:
        first_row = group.iloc[0]
        issuer, doc_type, classification, evidence = determine_issuer_and_type(first_row)
        
        if classification == "INTERNAL_POLICY":
            internal_count += 1
        else:
            external_count += 1

        doc_catalog.append({
            "document_id": doc_id,
            "title": first_row.get("title", doc_id),
            "citation_code": first_row.get("citation_code", ""),
            "document_type": doc_type,
            "issuer": issuer,
            "classification": classification,
            "evidence": evidence,
            "chunk_count": len(group),
        })

    is_sufficient = (internal_count > 0 and external_count > 0)

    # Generate Markdown Report
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "gap_input_catalog.md"

    lines = [
        "# BÁO CÁO PHÂN LOẠI DANH MỤC TÀI LIỆU GAP ANALYSIS (GAP INPUT CATALOG)",
        "",
        "- **Ngày thực hiện**: 2026-08-25",
        "- **Môi trường thực thi**: `buoi_17/`",
        "- **Dữ liệu nguồn**: `../buoi_16/data/processed/chunks_secure.csv`",
        f"- **Tổng số Văn bản (Documents)**: **{total_docs}** văn bản ({len(df)} chunks)",
        f"- **Số văn bản Quy định Bên ngoài (`EXTERNAL_REQUIREMENT`)**: **{external_count}** văn bản",
        f"- **Số văn bản Quy định Nội bộ (`INTERNAL_POLICY`)**: **{internal_count}** văn bản",
        "",
        "---",
        "",
        "## 1. Bảng Danh mục Chi tiết Toàn bộ Văn bản trong Corpus",
        "",
        "| Document ID | Số hiệu / Trích dẫn | Loại văn bản | Cơ quan ban hành | Phân loại (Classification) | Bằng chứng Phân loại (Evidence) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for d in doc_catalog:
        lines.append(
            f"| `{d['document_id']}` | `{d['citation_code']}` | {d['document_type']} | {d['issuer']} | **{d['classification']}** | {d['evidence']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 2. Kết luận Đánh giá Tính Sẵn sàng cho Compliance Gap Analysis",
        "",
    ])

    if is_sufficient:
        lines.extend([
            "Dữ liệu corpus chứa đầy đủ cả văn bản quy định nhà nước bên ngoài (`EXTERNAL_REQUIREMENT`) và văn bản quy trình nội bộ (`INTERNAL_POLICY`).",
            "",
            "COMPLIANCE GAP DATA: READY",
        ])
    else:
        lines.extend([
            "> [!WARNING]",
            "> **BÁO CÁO THIẾU DỮ LIỆU THỰC TẾ (DATA GAP IDENTIFIED)**:",
            "> - Toàn bộ 100% văn bản trong corpus hiện tại (`chunks_secure.csv`) đều là **Văn bản Quy phạm Pháp luật của Nhà nước** (Luật của Quốc hội, Nghị định của Chính phủ, Thông tư của NHNN/BTC).",
            "> - Tập dữ liệu **CHƯA CÓ bất kỳ văn bản Quy định / Quy trình Vận hành Nội bộ (`INTERNAL_POLICY`) nào của Ngân hàng Thương mại**.",
            "> - Theo nguyên tắc kiểm toán dữ liệu nghiêm ngặt của Buổi 17, hệ thống **TUYỆT ĐỐI KHÔNG gán nhãn giả** cho một Thông tư/Nghị định khác để coi đó là 'quy định nội bộ' nhằm mục đích chạy demo.",
            "",
            "---",
            "",
            "COMPLIANCE GAP DATA: INSUFFICIENT",
            "DATA GAP: INTERNAL POLICY NOT FOUND",
        ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[+] Gap input catalog generated at: {report_path}")
    if is_sufficient:
        print("COMPLIANCE GAP DATA: READY")
    else:
        print("COMPLIANCE GAP DATA: INSUFFICIENT")
        print("DATA GAP: INTERNAL POLICY NOT FOUND")


if __name__ == "__main__":
    main()
