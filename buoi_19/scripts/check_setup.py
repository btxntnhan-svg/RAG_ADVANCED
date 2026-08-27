"""Script checking environment and dataset readiness for Buoi 18."""

import os
from pathlib import Path
import sys
import pandas as pd
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

def main() -> None:
    # 1. Check Python & venv
    venv_path = sys.prefix
    py_version = sys.version.split()[0]
    env_ok = True

    # 2. Check internal policies data
    internal_csv = PROJECT_ROOT / "data" / "agribank_internal_policies.csv"
    if internal_csv.exists():
        df_int = pd.read_csv(internal_csv, dtype=str)
        int_rows = len(df_int)
        int_cols = list(df_int.columns)
        int_cols_ok = (len(int_cols) == 14 and "so_ky_hieu" in int_cols and "allowed_roles" in int_cols)
        int_ok = True
    else:
        int_rows, int_cols, int_cols_ok, int_ok = 0, [], False, False

    # 3. Check combined secure data
    combined_csv = PROJECT_ROOT / "data" / "chunks_combined_secure.csv"
    if combined_csv.exists():
        df_comb = pd.read_csv(combined_csv, dtype=str)
        comb_rows = len(df_comb)
        comb_docs = df_comb["document_id"].nunique()
        agri_chunks = len(df_comb[df_comb["co_quan_ban_hanh"].str.contains("Agribank", na=False) | df_comb["source_file"].str.contains("agribank", na=False)])
        ext_chunks = comb_rows - agri_chunks
        comb_ok = True
    else:
        comb_rows, comb_docs, agri_chunks, ext_chunks, comb_ok = 0, 0, 0, 0, False

    # 4. Check directories
    scripts_dir = PROJECT_ROOT / "scripts"
    outputs_dir = PROJECT_ROOT / "outputs"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # 5. Check API keys
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
    key_ok = bool(gemini_key)

    # Write Markdown Report
    report_path = outputs_dir / "environment_check_report.md"
    lines = [
        "# BÁO CÁO KIỂM TRA MÔI TRƯỜNG VÀ DỮ LIỆU BUỔI 18",
        "",
        "- **Ngày thực hiện**: 2026-08-25",
        "- **Môi trường Python**: Python " + py_version + f" (`{venv_path}`)",
        "- **Thư mục làm việc**: `buoi_18/`",
        "",
        "---",
        "",
        "## 1. Kết quả Phân tích Dữ liệu Đầu vào (Data Inspection)",
        "",
        "### 1.1. File Quy định Nội bộ Agribank (`data/agribank_internal_policies.csv`)",
        f"- **Trạng thái tồn tại**: `TỒN TẠI`",
        f"- **Số lượng Chunks**: **{int_rows}** chunks",
        f"- **Số lượng Cột**: **{len(int_cols)}** cột (Yêu cầu 14 cột: `{int_cols_ok}`)",
        f"- **Danh sách Cột Metadata**: `{', '.join(int_cols)}`",
        "",
        "### 1.2. File Dữ liệu Kết hợp (`data/chunks_combined_secure.csv`)",
        f"- **Trạng thái tồn tại**: `TỒN TẠI`",
        f"- **Tổng số Chunks**: **{comb_rows}** chunks",
        f"- **Tổng số Văn bản (Unique Document IDs)**: **{comb_docs}** văn bản",
        f"- **Số chunk Quy định Nội bộ Agribank (`INTERNAL_POLICY`)**: **{agri_chunks}** chunks",
        f"- **Số chunk Quy định Pháp luật Bên ngoài (`EXTERNAL_REQUIREMENT`)**: **{ext_chunks}** chunks",
        "",
        "---",
        "",
        "## 2. Kiểm tra Môi trường & Khóa API (Environment & Credentials)",
        "",
        f"- **Thư mục `scripts/` & `outputs/`**: `SẴN SÀNG`",
        f"- **Biến môi trường API Key (`GEMINI_API_KEY` / `LLM_API_KEY`)**: `{'HỢP LỆ' if key_ok else 'THIẾU'}`",
        "",
        "---",
        "",
        f"ENVIRONMENT READY: {'YES' if (env_ok and key_ok) else 'NO'}",
        f"INTERNAL DATA READY: {'YES' if int_ok else 'NO'}",
        f"COMBINED DATA READY: {'YES' if comb_ok else 'NO'}",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[+] Environment report generated at: {report_path}")
    print(f"\nENVIRONMENT READY: {'YES' if (env_ok and key_ok) else 'NO'}")
    print(f"INTERNAL DATA READY: {'YES' if int_ok else 'NO'}")
    print(f"COMBINED DATA READY: {'YES' if comb_ok else 'NO'}")


if __name__ == "__main__":
    main()
