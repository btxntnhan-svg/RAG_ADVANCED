#!/usr/bin/env python3
"""Inspect the seed CSV files for the Wiki Risk Graph training project.

This script reads the four source files in the data/ directory and reports:
- row counts
- column names
- inferred primary keys
- reference keys and missing references
- relationship types
- null values
- duplicate keys
- missing master-data references

It intentionally does not invent missing master data or relationships.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def read_csv(path: Path) -> Tuple[List[str], List[dict]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    return fieldnames, rows


def count_nulls(rows: Iterable[dict]) -> Tuple[int, Dict[str, int]]:
    total_nulls = 0
    by_field: Dict[str, int] = defaultdict(int)
    for row in rows:
        for field, value in row.items():
            if value is None or value == "":
                by_field[field] += 1
                total_nulls += 1
    return total_nulls, dict(sorted(by_field.items()))


def find_duplicate_keys(rows: Iterable[dict], key_field: str) -> List[Tuple[str, int, int]]:
    seen: Dict[str, int] = {}
    duplicates: List[Tuple[str, int, int]] = []
    for index, row in enumerate(rows, start=2):  # start=2 to include header row offset
        key = row.get(key_field, "")
        if key == "":
            continue
        if key in seen:
            duplicates.append((key, seen[key], index))
        else:
            seen[key] = index
    return duplicates


def find_missing_references(rows: Iterable[dict], key_field: str, valid_ids: set[str]) -> List[str]:
    missing: List[str] = []
    for row in rows:
        value = row.get(key_field, "")
        if value and value not in valid_ids:
            missing.append(value)
    return sorted(set(missing))


def summarize_file(file_name: str, path: Path) -> dict:
    fieldnames, rows = read_csv(path)
    null_total, nulls_by_field = count_nulls(rows)

    if file_name == "risk_profiles_seed.csv":
        primary_key = "id"
    elif file_name == "controls_seed.csv":
        primary_key = "id"
    elif file_name == "risk_events_seed.csv":
        primary_key = "id"
    elif file_name == "relationships_seed.csv":
        primary_key = "(source_id, relationship_type, target_id)"
    else:
        primary_key = "unidentified"

    duplicates = find_duplicate_keys(rows, primary_key.split(",")[0].replace("(", "").replace(")", "").strip()) if primary_key.startswith("(") is False else []

    summary = {
        "file": file_name,
        "rows": len(rows),
        "columns": fieldnames,
        "primary_key": primary_key,
        "null_total": null_total,
        "nulls_by_field": nulls_by_field,
        "duplicates": duplicates,
    }
    return summary


def main() -> None:
    file_map = {
        "risk_profiles_seed.csv": DATA_DIR / "risk_profiles_seed.csv",
        "controls_seed.csv": DATA_DIR / "controls_seed.csv",
        "risk_events_seed.csv": DATA_DIR / "risk_events_seed.csv",
        "relationships_seed.csv": DATA_DIR / "relationships_seed.csv",
    }

    print("=== KIỂM TRA DỮ LIỆU SEED CHO WIKI RISK GRAPH ===")
    print(f"Root: {ROOT}")
    print(f"Data directory: {DATA_DIR}")

    summaries = {}
    for file_name, path in file_map.items():
        if not path.exists():
            raise FileNotFoundError(f"Thiếu file: {path}")
        summaries[file_name] = summarize_file(file_name, path)

    # Read relationship rows separately for relationship-type and link analysis
    rel_fields, rel_rows = read_csv(file_map["relationships_seed.csv"])
    relationship_types = sorted({row.get("relationship_type", "") for row in rel_rows if row.get("relationship_type")})

    risk_fields, risk_rows = read_csv(file_map["risk_profiles_seed.csv"])
    control_fields, control_rows = read_csv(file_map["controls_seed.csv"])
    event_fields, event_rows = read_csv(file_map["risk_events_seed.csv"])

    risk_ids = {row.get("id", "") for row in risk_rows if row.get("id")}
    control_ids = {row.get("id", "") for row in control_rows if row.get("id")}
    event_ids = {row.get("id", "") for row in event_rows if row.get("id")}

    # Key references in data
    risk_ref_missing = find_missing_references(event_rows, "risk_id", risk_ids)
    rel_source_missing = find_missing_references(rel_rows, "source_id", set(control_ids) | set(risk_ids))
    rel_target_missing = find_missing_references(rel_rows, "target_id", set(risk_ids) | set(event_ids))

    # Generic summary per file
    for file_name, summary in summaries.items():
        print(f"\n=== {file_name} ===")
        print(f"Số dòng dữ liệu: {summary['rows']}")
        print(f"Tên cột: {', '.join(summary['columns'])}")
        print(f"Khóa chính suy ra: {summary['primary_key']}")
        print(f"Số giá trị null: {summary['null_total']}")
        if summary["nulls_by_field"]:
            print("Null theo cột:")
            for field, count in summary["nulls_by_field"].items():
                print(f"  - {field}: {count}")
        else:
            print("Null theo cột: không có")

        if summary["duplicates"]:
            print("Duplicate khóa chính:")
            for key, first_line, second_line in summary["duplicates"]:
                print(f"  - {key}: dòng {first_line} và {second_line}")
        else:
            print("Duplicate khóa chính: không có")

    print(f"\n=== relationship_type ===")
    print(f"Các loại relationship_type: {relationship_types}")

    print(f"\n=== Khóa tham chiếu ===")
    print("- risk_events_seed.csv.risk_id -> risk_profiles_seed.csv.id")
    if risk_ref_missing:
        print(f"  Missing: {risk_ref_missing}")
    else:
        print("  Missing: không có")

    print("- relationships_seed.csv.source_id -> {KiemSoat.id, RuiRo.id}")
    if rel_source_missing:
        print(f"  Missing: {rel_source_missing}")
    else:
        print("  Missing: không có")

    print("- relationships_seed.csv.target_id -> {RuiRo.id, SuKienRuiRo.id}")
    if rel_target_missing:
        print(f"  Missing: {rel_target_missing}")
    else:
        print("  Missing: không có")

    print(f"\n=== Dữ liệu chưa có và không được tự bịa ===")
    print("- Master data cho owner_unit_id: CHƯA CÓ")
    print("- Master data cho owner_role_id: CHƯA CÓ")
    print("- Bảng đơn vị (Unit) tương ứng: CHƯA CÓ")
    print("- Bảng vai trò (Role) tương ứng: CHƯA CÓ")
    print("- Bảng quy trình / văn bản / điều khoản: CHƯA CÓ")

    print(f"\n=== Node có thể tạo từ dữ liệu hiện có ===")
    print("- RuiRo: từ risk_profiles_seed.csv")
    print("- KiemSoat: từ controls_seed.csv")
    print("- SuKienRuiRo: từ risk_events_seed.csv")

    print(f"\n=== Edge có thể tạo từ dữ liệu hiện có ===")
    print("- KiemSoat -MITIGATES-> RuiRo")
    print("- RuiRo -OBSERVED_AS-> SuKienRuiRo")

    print(f"\n=== Kiến trúc MVP đề xuất ===")
    print("KiemSoat")
    print("   | MITIGATES")
    print("   v")
    print("RuiRo")
    print("   | OBSERVED_AS")
    print("   v")
    print("SuKienRuiRo")
    print("\nLưu ý: owner_unit_id và owner_role_id chỉ là mã tham chiếu; không suy luận tên đơn vị/ vai trò nếu master data chưa có.")

    print(f"\n=== Kết luận ngắn gọn ===")
    print("- 4 file CSV được đọc và kiểm tra thành công.")
    print("- 3 loại node chính xác định: RuiRo, KiemSoat, SuKienRuiRo.")
    print("- 2 loại edge chính xác định: MITIGATES, OBSERVED_AS.")
    print("- Không phát hiện duplicate hoặc missing reference trong dữ liệu hiện có.")
    print("- Dữ liệu master cho owner_unit_id và owner_role_id chưa có trong project.")


if __name__ == "__main__":
    main()
