#!/usr/bin/env python3
"""Build normalized entity and relation datasets from the risk graph seed CSV files.

This script reads the four source CSV files under data/, creates a normalized
entities.csv dataset, and creates relations.csv from relationship records.
It validates that relationship references point to entity IDs that actually exist.
The script does not invent new relationships or master-data names.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"

SOURCE_MAP = {
    "risk_profiles_seed.csv": "RuiRo",
    "controls_seed.csv": "KiemSoat",
    "risk_events_seed.csv": "SuKienRuiRo",
}

ENTITY_FIELD_ORDER = [
    "id",
    "type",
    "name",
    "description",
    "source_file",
    "data_origin",
    "verification_status",
    "category",
    "cause",
    "event",
    "impact",
    "inherent_level",
    "residual_level",
    "owner_unit_id",
    "control_type",
    "frequency",
    "owner_role_id",
    "effectiveness",
    "risk_id",
    "occurred_at",
    "discovered_at",
    "severity",
    "loss_amount_vnd",
]

RELATION_FIELD_ORDER = [
    "source_id",
    "relationship_type",
    "target_id",
    "source",
    "evidence_quote",
    "confidence",
    "verification_status",
    "data_origin",
]


def read_csv_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_entity_row(source_file: str, row: dict) -> dict:
    entity_type = SOURCE_MAP.get(source_file, "Unknown")
    record = {
        "id": row.get("id", ""),
        "type": entity_type,
        "name": row.get("name", ""),
        "description": row.get("description", ""),
        "source_file": source_file,
        "data_origin": row.get("data_origin", ""),
        "verification_status": row.get("verification_status", ""),
    }

    if source_file == "risk_profiles_seed.csv":
        record.update({
            "category": row.get("category", ""),
            "cause": row.get("cause", ""),
            "event": row.get("event", ""),
            "impact": row.get("impact", ""),
            "inherent_level": row.get("inherent_level", ""),
            "residual_level": row.get("residual_level", ""),
            "owner_unit_id": row.get("owner_unit_id", ""),
        })
    elif source_file == "controls_seed.csv":
        record.update({
            "control_type": row.get("control_type", ""),
            "frequency": row.get("frequency", ""),
            "owner_role_id": row.get("owner_role_id", ""),
            "effectiveness": row.get("effectiveness", ""),
        })
    elif source_file == "risk_events_seed.csv":
        record.update({
            "risk_id": row.get("risk_id", ""),
            "occurred_at": row.get("occurred_at", ""),
            "discovered_at": row.get("discovered_at", ""),
            "severity": row.get("severity", ""),
            "loss_amount_vnd": row.get("loss_amount_vnd", ""),
        })

    return record


def build_entities() -> list[dict]:
    entity_rows: list[dict] = []
    for source_file, entity_type in SOURCE_MAP.items():
        path = DATA_DIR / source_file
        if not path.exists():
            raise FileNotFoundError(f"Thiếu file nguồn: {path}")

        for row in read_csv_rows(path):
            entity_row = normalize_entity_row(source_file, row)
            if not entity_row["id"]:
                continue
            entity_rows.append(entity_row)
    return entity_rows


def build_relations() -> list[dict]:
    path = DATA_DIR / "relationships_seed.csv"
    if not path.exists():
        raise FileNotFoundError(f"Thiếu file quan hệ: {path}")

    relation_rows: list[dict] = []
    for row in read_csv_rows(path):
        relation = {
            "source_id": row.get("source_id", ""),
            "relationship_type": row.get("relationship_type", ""),
            "target_id": row.get("target_id", ""),
            "source": row.get("source", ""),
            "evidence_quote": row.get("evidence_quote", ""),
            "confidence": row.get("confidence", ""),
            "verification_status": row.get("verification_status", ""),
            "data_origin": row.get("data_origin", ""),
        }
        relation_rows.append(relation)
    return relation_rows


def validate_references(entity_rows: list[dict], relation_rows: list[dict]) -> list[dict]:
    entity_ids = {row["id"] for row in entity_rows}
    orphan_rows: list[dict] = []
    for relation in relation_rows:
        source_id = relation.get("source_id", "")
        target_id = relation.get("target_id", "")
        if source_id not in entity_ids or target_id not in entity_ids:
            orphan_rows.append(relation)
    return orphan_rows


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    entity_rows = build_entities()
    relation_rows = build_relations()

    # Write outputs
    write_csv(OUTPUT_DIR / "entities.csv", ENTITY_FIELD_ORDER, entity_rows)
    write_csv(OUTPUT_DIR / "relations.csv", RELATION_FIELD_ORDER, relation_rows)

    entity_count_by_type = Counter(row["type"] for row in entity_rows)
    relation_count_by_type = Counter(row["relationship_type"] for row in relation_rows)
    orphans = validate_references(entity_rows, relation_rows)

    print("=== BUILD ENTITIES / RELATIONS ===")
    print(f"Số entity tổng: {len(entity_rows)}")
    print("Entity theo type:")
    for entity_type, count in sorted(entity_count_by_type.items()):
        print(f"  - {entity_type}: {count}")

    print(f"\nSố relation tổng: {len(relation_rows)}")
    print("Relation theo relationship_type:")
    for rel_type, count in sorted(relation_count_by_type.items()):
        print(f"  - {rel_type}: {count}")

    if orphans:
        print("\nERROR: orphan reference found.")
        for orphan in orphans:
            print(
                f"  - source_id={orphan.get('source_id')} target_id={orphan.get('target_id')} "
                f"relationship_type={orphan.get('relationship_type')}"
            )
        return 1

    print("\nNo orphan reference found in relations.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
