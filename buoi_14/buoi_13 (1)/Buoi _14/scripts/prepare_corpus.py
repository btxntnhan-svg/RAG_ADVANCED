#!/usr/bin/env python3
"""Prepare a shared normalized corpus for BM25, dense, hybrid, and reranking.

This script reads the source files under ../kb+hops/ if present and writes a common
normalized CSV to buoi_14/data/processed/chunks_normalized.csv.

It does not modify the source data in ../kb+hops/.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT.parent / "kb+hops"
OUTPUT_PATH = ROOT / "data" / "processed" / "chunks_normalized.csv"

REQUIRED_FIELDS = [
    "chunk_id",
    "document_id",
    "text",
    "source_file",
    "title",
    "document_type",
    "chapter",
    "section",
    "article",
    "clause",
    "effective_date",
    "status",
]


def detect_encoding(path: Path) -> str:
    for candidate in ("utf-8-sig", "utf-8", "cp1258", "latin-1"):
        try:
            with path.open("r", encoding=candidate, newline="") as handle:
                handle.read(2048)
            return candidate
        except Exception:
            continue
    return "utf-8"


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    encoding = detect_encoding(path)
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r", " ").replace("\n", " ")
    text = " ".join(text.split())
    return text.strip()


def first_present(row: dict, candidates: Iterable[str]) -> str:
    for key in candidates:
        if key in row and row.get(key) not in (None, ""):
            return str(row.get(key))
    return ""


def normalize_metadata(value: object) -> str:
    return clean_text(value)


def pick_document_id(row: dict) -> str:
    candidates = [
        "document_id",
        "doc_id",
        "id",
        "documentId",
        "docId",
        "source_id",
        "document",
    ]
    value = first_present(row, candidates)
    return value or "unknown_document"


def pick_text_field(row: dict) -> str:
    candidates = [
        "text",
        "content",
        "body",
        "chunk_text",
        "article_text",
        "section_text",
        "paragraph",
        "content_text",
        "description",
        "excerpt",
    ]
    return first_present(row, candidates)


def pick_chunk_id(row: dict, document_id: str, index: int) -> str:
    for key in ["chunk_id", "id", "chunkId", "segment_id", "segmentId", "content_id"]:
        if key in row and row.get(key) not in (None, ""):
            return str(row.get(key))
    return f"{document_id or 'doc'}-{index:05d}"


def ensure_out_dir() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def build_output_rows() -> tuple[list[dict], dict, int]:
    source_files = {
        "metadata.csv": SRC_DIR / "metadata.csv",
        "content.csv": SRC_DIR / "content.csv",
        "relationships.csv": SRC_DIR / "relationships.csv",
    }

    missing_sources = [name for name, path in source_files.items() if not path.exists()]
    if missing_sources:
        raise FileNotFoundError(
            "Thiếu dữ liệu nguồn trong ../kb+hops/. "
            f"Các file còn thiếu: {', '.join(missing_sources)}. "
            "Đặt thư mục kb+hops cùng cấp với buoi_14 và chạy lại."
        )

    metadata_rows = read_csv(source_files["metadata.csv"])
    content_rows = read_csv(source_files["content.csv"])
    _ = read_csv(source_files["relationships.csv"])  # kept for provenance and future graph work

    meta_by_document: dict[str, dict] = {}
    for row in metadata_rows:
        doc_id = pick_document_id(row)
        meta_by_document.setdefault(doc_id, {})
        meta_by_document[doc_id].update(row)

    all_rows: list[dict] = []
    seen_chunk_ids: set[str] = set()
    duplicate_chunk_ids: set[str] = set()
    missing_text_count = 0

    for idx, row in enumerate(content_rows, start=1):
        document_id = pick_document_id(row)
        text = pick_text_field(row)
        if not text:
            text = ""
        if not text:
            missing_text_count += 1

        chunk_id = pick_chunk_id(row, document_id, idx)
        if chunk_id in seen_chunk_ids:
            duplicate_chunk_ids.add(chunk_id)
        seen_chunk_ids.add(chunk_id)

        metadata = meta_by_document.get(document_id, {})
        record = {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "text": clean_text(text),
            "source_file": "content.csv",
            "title": normalize_metadata(metadata.get("title") or metadata.get("document_title") or metadata.get("name")),
            "document_type": normalize_metadata(metadata.get("document_type") or metadata.get("type")),
            "chapter": normalize_metadata(metadata.get("chapter") or metadata.get("chapter_no")),
            "section": normalize_metadata(metadata.get("section") or metadata.get("section_name")),
            "article": normalize_metadata(metadata.get("article") or metadata.get("article_no")),
            "clause": normalize_metadata(metadata.get("clause") or metadata.get("clause_no")),
            "effective_date": normalize_metadata(metadata.get("effective_date") or metadata.get("date")),
            "status": normalize_metadata(metadata.get("status") or metadata.get("state")),
        }
        all_rows.append(record)

    unique_doc_ids = sorted({row["document_id"] for row in all_rows if row["document_id"]})
    stats = {
        "total_chunks": len(all_rows),
        "total_documents": len(unique_doc_ids),
        "missing_text": missing_text_count,
        "duplicates": sorted(duplicate_chunk_ids),
    }
    return all_rows, stats, len([])


def write_csv(rows: list[dict], output_path: Path) -> None:
    ensure_out_dir()
    fieldnames = REQUIRED_FIELDS
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def print_summary(rows: list[dict], stats: dict) -> None:
    print("=== PREPARE CORPUS ===")
    print(f"Tổng số chunk: {stats['total_chunks']}")
    print(f"Số document: {stats['total_documents']}")
    print(f"Số chunk thiếu text: {stats['missing_text']}")
    print(f"Duplicate chunk_id: {stats['duplicates'] if stats['duplicates'] else 'không có'}")

    samples = rows[:3]
    print("3 sample record:")
    for sample in samples:
        print(sample)


def main() -> int:
    try:
        rows, stats, _ = build_output_rows()
    except FileNotFoundError as exc:
        ensure_out_dir()
        output_path = OUTPUT_PATH
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REQUIRED_FIELDS)
            writer.writeheader()
        print(f"ERROR: {exc}")
        print(f"Đã tạo file rỗng: {output_path}")
        return 1

    write_csv(rows, OUTPUT_PATH)
    print_summary(rows, stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
