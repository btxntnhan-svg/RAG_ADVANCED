#!/usr/bin/env python3
"""Build Obsidian-friendly Markdown pages from the normalized entity and relation CSVs."""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTITIES_PATH = ROOT / "outputs" / "entities.csv"
RELATIONS_PATH = ROOT / "outputs" / "relations.csv"
WIKI_DIR = ROOT / "wiki"
RISK_DIR = WIKI_DIR / "risks"
CONTROL_DIR = WIKI_DIR / "controls"
EVENT_DIR = WIKI_DIR / "events"


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def normalize_filename(value: str, fallback: str = "untitled") -> str:
    text = (value or fallback).strip()
    text = re.sub(r"[<>:\"/\\|?*]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.rstrip(".")
    return text if text else fallback


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_frontmatter(entity: dict) -> str:
    return (
        "---\n"
        f"id: {entity.get('id', '')}\n"
        f"type: {entity.get('type', '')}\n"
        f"verification_status: {entity.get('verification_status', '')}\n"
        f"data_origin: {entity.get('data_origin', '')}\n"
        "---\n\n"
    )


def link_for(name: str) -> str:
    return f"[[{name}]]"


def build_risk_page(risk: dict, related_controls: list[dict], related_events: list[dict]) -> str:
    lines = [
        make_frontmatter(risk),
        f"# {risk.get('name', '')}\n\n",
        f"**ID:** {risk.get('id', '')}\n",
        f"**Type:** {risk.get('type', '')}\n",
        f"**Verification status:** {risk.get('verification_status', '')}\n",
        f"**Data origin:** {risk.get('data_origin', '')}\n",
    ]

    for label, value in [
        ("Description", risk.get("description", "")),
        ("Category", risk.get("category", "")),
        ("Cause", risk.get("cause", "")),
        ("Event", risk.get("event", "")),
        ("Impact", risk.get("impact", "")),
        ("Inherent level", risk.get("inherent_level", "")),
        ("Residual level", risk.get("residual_level", "")),
        ("Owner unit ID", risk.get("owner_unit_id", "")),
    ]:
        if value:
            lines.append(f"**{label}:** {value}\n")

    lines.append("\n## Kiểm soát liên quan\n")
    if related_controls:
        for relation in related_controls:
            control_name = relation.get("control_name", "")
            if control_name:
                lines.append(
                    f"- {link_for(control_name)} — "
                    f"relationship_type: {relation.get('relationship_type', '')}; "
                    f"verification_status: {relation.get('verification_status', '')}; "
                    f"evidence_quote: {relation.get('evidence_quote', '')}\n"
                )
    else:
        lines.append("- Chưa có dữ liệu kiểm soát liên quan.\n")

    lines.append("\n## Sự kiện liên quan\n")
    if related_events:
        for relation in related_events:
            event_name = relation.get("event_name", "")
            if event_name:
                lines.append(
                    f"- {link_for(event_name)} — "
                    f"relationship_type: {relation.get('relationship_type', '')}; "
                    f"verification_status: {relation.get('verification_status', '')}; "
                    f"evidence_quote: {relation.get('evidence_quote', '')}\n"
                )
    else:
        lines.append("- Chưa có dữ liệu sự kiện liên quan.\n")

    return "".join(lines)


def build_control_page(control: dict, related_risks: list[dict]) -> str:
    lines = [
        make_frontmatter(control),
        f"# {control.get('name', '')}\n\n",
        f"**ID:** {control.get('id', '')}\n",
        f"**Type:** {control.get('type', '')}\n",
        f"**Verification status:** {control.get('verification_status', '')}\n",
        f"**Data origin:** {control.get('data_origin', '')}\n",
    ]

    for label, value in [
        ("Control type", control.get("control_type", "")),
        ("Frequency", control.get("frequency", "")),
        ("Owner role ID", control.get("owner_role_id", "")),
        ("Effectiveness", control.get("effectiveness", "")),
    ]:
        if value:
            lines.append(f"**{label}:** {value}\n")

    lines.append("\n## Giảm thiểu rủi ro\n")
    if related_risks:
        for relation in related_risks:
            risk_name = relation.get("risk_name", "")
            if risk_name:
                lines.append(
                    f"- {link_for(risk_name)} — "
                    f"relationship_type: {relation.get('relationship_type', '')}; "
                    f"verification_status: {relation.get('verification_status', '')}; "
                    f"evidence_quote: {relation.get('evidence_quote', '')}\n"
                )
    else:
        lines.append("- Chưa có rủi ro nào được liên kết bằng quan hệ MITIGATES.\n")

    return "".join(lines)


def build_event_page(event: dict, related_risk: dict | None) -> str:
    lines = [
        make_frontmatter(event),
        f"# {event.get('name', '')}\n\n",
        f"**ID:** {event.get('id', '')}\n",
        f"**Type:** {event.get('type', '')}\n",
        f"**Verification status:** {event.get('verification_status', '')}\n",
        f"**Data origin:** {event.get('data_origin', '')}\n",
    ]

    for label, value in [
        ("Risk ID", event.get("risk_id", "")),
        ("Occurred at", event.get("occurred_at", "")),
        ("Discovered at", event.get("discovered_at", "")),
        ("Severity", event.get("severity", "")),
        ("Loss amount VND", event.get("loss_amount_vnd", "")),
        ("Description", event.get("description", "")),
    ]:
        if value:
            lines.append(f"**{label}:** {value}\n")

    lines.append("\n## Rủi ro liên quan\n")
    if related_risk:
        lines.append(
            f"- {link_for(related_risk.get('name', ''))} — "
            f"relationship_type: OBSERVED_AS; "
            f"verification_status: {related_risk.get('verification_status', '')}\n"
        )
    else:
        lines.append("- Chưa có rủi ro liên kết.\n")

    return "".join(lines)


def build_home_page(entity_count: int, relation_count: int, by_type: dict[str, int]) -> str:
    lines = [
        "# Wiki Risk Graph\n\n",
        "## Tổng quan\n",
        "- [Danh sách rủi ro](risks/)\n",
        "- [Danh sách kiểm soát](controls/)\n",
        "- [Danh sách sự kiện](events/)\n",
        "\n## Thống kê\n",
        f"- Tổng số node: {entity_count}\n",
        f"- Tổng số edge: {relation_count}\n",
        f"- Số rủi ro: {by_type.get('RuiRo', 0)}\n",
        f"- Số kiểm soát: {by_type.get('KiemSoat', 0)}\n",
        f"- Số sự kiện: {by_type.get('SuKienRuiRo', 0)}\n",
    ]
    return "".join(lines)


def main() -> int:
    entities = read_csv(ENTITIES_PATH)
    relations = read_csv(RELATIONS_PATH)

    if not entities:
        raise ValueError(f"Không có Entity nào trong {ENTITIES_PATH}")
    if not relations:
        raise ValueError(f"Không có Relation nào trong {RELATIONS_PATH}")

    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    for subdir in (RISK_DIR, CONTROL_DIR, EVENT_DIR):
        subdir.mkdir(parents=True, exist_ok=True)

    entity_by_id = {entity.get('id', ''): entity for entity in entities if entity.get('id')}
    entity_name_by_id = {entity.get('id', ''): entity.get('name', '') for entity in entities if entity.get('id')}

    risk_relations_by_target: dict[str, list[dict]] = {}
    risk_relations_by_source: dict[str, list[dict]] = {}
    control_relations_by_source: dict[str, list[dict]] = {}
    event_relations_by_target: dict[str, dict] = {}

    for relation in relations:
        source_id = relation.get('source_id', '')
        target_id = relation.get('target_id', '')
        rel_type = relation.get('relationship_type', '')

        if rel_type == 'MITIGATES' and target_id:
            risk_relations_by_target.setdefault(target_id, []).append({
                **relation,
                'control_name': entity_name_by_id.get(source_id, source_id),
            })
            control_relations_by_source.setdefault(source_id, []).append({
                **relation,
                'risk_name': entity_name_by_id.get(target_id, target_id),
            })
        if rel_type == 'OBSERVED_AS' and source_id:
            risk_relations_by_source.setdefault(source_id, []).append({
                **relation,
                'event_name': entity_name_by_id.get(target_id, target_id),
            })
            event_relations_by_target[target_id] = {
                **relation,
                'risk_name': entity_name_by_id.get(source_id, source_id),
            }

    by_type = {}
    for entity in entities:
        entity_type = entity.get('type', '')
        by_type[entity_type] = by_type.get(entity_type, 0) + 1

    created_pages = []

    # Home page
    home_path = WIKI_DIR / "Home.md"
    write_markdown(home_path, build_home_page(len(entities), len(relations), by_type))
    created_pages.append(home_path)

    # Risk pages
    for entity in sorted(entities, key=lambda row: row.get('id', '')):
        if entity.get('type') != 'RuiRo':
            continue
        page_name = normalize_filename(entity.get('name', entity.get('id', 'untitled')))
        page_path = RISK_DIR / f"{page_name}.md"
        risk_page = build_risk_page(
            entity,
            risk_relations_by_target.get(entity.get('id', ''), []),
            risk_relations_by_source.get(entity.get('id', ''), []),
        )
        write_markdown(page_path, risk_page)
        created_pages.append(page_path)

    # Control pages
    for entity in sorted(entities, key=lambda row: row.get('id', '')):
        if entity.get('type') != 'KiemSoat':
            continue
        page_name = normalize_filename(entity.get('name', entity.get('id', 'untitled')))
        page_path = CONTROL_DIR / f"{page_name}.md"
        control_page = build_control_page(entity, control_relations_by_source.get(entity.get('id', ''), []))
        write_markdown(page_path, control_page)
        created_pages.append(page_path)

    # Event pages
    for entity in sorted(entities, key=lambda row: row.get('id', '')):
        if entity.get('type') != 'SuKienRuiRo':
            continue
        page_name = normalize_filename(entity.get('name', entity.get('id', 'untitled')))
        page_path = EVENT_DIR / f"{page_name}.md"
        related_risk = None
        if entity.get('id') in event_relations_by_target:
            related_risk = entity_by_id.get(event_relations_by_target[entity['id']].get('risk_name', ''))
            if related_risk is None:
                related_risk = {'name': event_relations_by_target[entity['id']].get('risk_name', ''), 'verification_status': event_relations_by_target[entity['id']].get('verification_status', '')}
        event_page = build_event_page(entity, related_risk)
        write_markdown(page_path, event_page)
        created_pages.append(page_path)

    # Count wikilinks
    wiki_markdown_files = sorted(WIKI_DIR.rglob("*.md"))
    wiki_link_count = 0
    for md_file in wiki_markdown_files:
        content = md_file.read_text(encoding="utf-8")
        wiki_link_count += len(re.findall(r"\[\[([^\]]+)\]\]", content))

    # Example path: first control -> first risk -> first event
    first_control = next((entity for entity in entities if entity.get('type') == 'KiemSoat'), None)
    first_risk = next((entity for entity in entities if entity.get('type') == 'RuiRo'), None)
    first_event = next((entity for entity in entities if entity.get('type') == 'SuKienRuiRo'), None)

    if first_control and first_risk and first_event:
        example_path = f"{first_control['name']} -> {first_risk['name']} -> {first_event['name']}"
    else:
        example_path = "Không đủ dữ liệu để dựng ví dụ đường đi."

    print("=== BUILD WIKI ===")
    print(f"Số trang Wiki đã tạo: {len(created_pages)}")
    print(f"Số wikilink: {wiki_link_count}")
    print(f"Ví dụ đường đi: {example_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
