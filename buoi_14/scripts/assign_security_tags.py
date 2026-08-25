"""Assign RBAC metadata to the normalized Buoi 14 retrieval corpus."""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import ROLES, validate_roles


INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "chunks_normalized.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "chunks_secure.csv"

HR_ROLES = validate_roles(("Admin", "HR"))
RISK_ROLES = validate_roles(("Admin", "Staff"))
GENERAL_ROLES = validate_roles(ROLES)

HR_KEYWORDS = (
    "tuyen dung",
    "bo nhiem",
    "ky luat",
    "luong thuong",
    "tien luong",
    "che do phu cap",
)
RISK_KEYWORDS = (
    "tin dung",
    "rui ro",
    "han muc",
    "phe duyet vay",
    "thu hoi no",
    "no xau",
)
REQUIRED_COLUMNS = {"document_id", "text"}


def normalize_for_matching(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(character for character in text if not unicodedata.combining(character))
    return " ".join(text.casefold().split())


RISK_DOCUMENT_IDS = {"177271", "168220", "174218", "117310", "185630"}
HR_DOCUMENT_IDS = {"112025", "163441", "166269"}


def classify_security(row: pd.Series) -> tuple[str, tuple[str, ...]]:
    doc_id = str(row.get("document_id", ""))
    metadata = " ".join(str(row.get(column, "")) for column in ("document_id", "title", "document_type"))
    full_text = str(row.get("text", ""))
    searchable = normalize_for_matching(metadata + " " + full_text)

    # 1. Match Risk documents by ID or specific credit/risk title keywords
    if doc_id in RISK_DOCUMENT_IDS or any(keyword in searchable for keyword in ("quyn tin dung", "an toan von", "phe duyet vay", "thu hoi no")):
        return "Risk", RISK_ROLES

    # 2. Match HR documents by ID or HR title keywords
    if doc_id in HR_DOCUMENT_IDS or any(keyword in searchable for keyword in ("tuyen dung", "bo nhiem", "ky luat", "tien luong")):
        return "HR", HR_ROLES

    # 3. Default to General
    return "General", GENERAL_ROLES


def assign_security_tags(dataframe: pd.DataFrame) -> pd.DataFrame:
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Input CSV is missing required columns: {missing}")

    tagged = dataframe.copy()
    classifications = tagged.apply(classify_security, axis=1)
    tagged["security_class"] = classifications.map(lambda item: item[0])
    tagged["allowed_roles"] = classifications.map(lambda item: json.dumps(item[1], ensure_ascii=False))
    return tagged


def validate_security_tags(tagged: pd.DataFrame) -> None:
    if tagged.empty:
        raise ValueError("Tagged corpus is empty")

    parsed_roles = tagged["allowed_roles"].map(json.loads)
    if parsed_roles.map(lambda roles: not roles or not all(role in ROLES for role in roles)).any():
        raise ValueError("Every chunk must have at least one valid allowed role")

def print_report(tagged: pd.DataFrame, output_path: Path) -> None:
    print(f"chunks_tagged: {len(tagged)}")
    print("security_class_counts:")
    for security_class, count in Counter(tagged["security_class"]).most_common():
        print(f"  {security_class}: {count}")

    print("representative_samples:")
    for security_class in ("HR", "Risk", "General"):
        samples = tagged.loc[tagged["security_class"] == security_class]
        if samples.empty:
            print(f"  {security_class}: unavailable in source corpus")
        else:
            sample = samples.iloc[0]
            print(
                f"  {security_class}: document_id={sample['document_id']}, "
                f"allowed_roles={sample['allowed_roles']}"
            )
    print(f"output: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    dataframe = pd.read_csv(args.input)
    tagged = assign_security_tags(dataframe)
    validate_security_tags(tagged)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tagged.to_csv(args.output, index=False, encoding="utf-8")
    print_report(tagged, args.output)


if __name__ == "__main__":
    main()