#!/usr/bin/env python3
"""Validate the generated wiki against the normalized entity/relation CSV outputs."""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI_ROOT = ROOT / "wiki"
ENTITIES_PATH = ROOT / "outputs" / "entities.csv"
RELATIONS_PATH = ROOT / "outputs" / "relations.csv"
REPORT_PATH = ROOT / "outputs" / "wiki_validation_report.md"


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_name(value: str) -> str:
    text = (value or "").strip()
    text = re.sub(r"[<>:\"/\\|?*]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.rstrip(".")
    return text.casefold()


def find_markdown_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def extract_frontmatter_id(content: str) -> str:
    match = re.search(r"^---\s*\n(.*?)(?:\n---\s*\n|\n---\s*$)", content, re.DOTALL)
    if not match:
        return ""
    body = match.group(1)
    for line in body.splitlines():
        if line.startswith("id:"):
            return line.split(":", 1)[1].strip()
    return ""


def count_wikilinks(content: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def page_to_file_lookup(wiki_root: Path) -> dict[str, Path]:
    lookup: dict[str, Path] = {}
    for path in find_markdown_files(wiki_root):
        name = normalize_name(path.stem)
        lookup.setdefault(name, path)
    return lookup


def validate() -> tuple[list[str], list[str], list[str], list[str], list[str], list[str], list[str], list[str], list[str]]:
    entity_rows = read_csv(ENTITIES_PATH)
    relation_rows = read_csv(RELATIONS_PATH)
    entity_ids = [row.get("id", "") for row in entity_rows if row.get("id")]
    entity_lookup = {row.get("id", ""): row for row in entity_rows if row.get("id")}

    entity_id_duplicates: list[str] = []
    seen: set[str] = set()
    for entity_id in entity_ids:
        if entity_id in seen:
            entity_id_duplicates.append(entity_id)
        seen.add(entity_id)

    wiki_files = find_markdown_files(WIKI_ROOT)
    page_lookup = page_to_file_lookup(WIKI_ROOT)
    page_records: list[dict] = []
    broken_links: list[str] = []
    pages_without_id: list[str] = []
    pages_not_in_entities: list[str] = []
    orphan_pages: list[str] = []
    all_wikilinks: list[str] = []

    for path in wiki_files:
        content = path.read_text(encoding="utf-8")
        page_id = extract_frontmatter_id(content)
        if page_id:
            page_records.append({"path": path, "id": page_id})
            if page_id not in entity_lookup:
                pages_not_in_entities.append(f"{path.relative_to(ROOT)} -> {page_id}")
        else:
            pages_without_id.append(str(path.relative_to(ROOT)))

        links = count_wikilinks(content)
        all_wikilinks.extend(links)
        for link in links:
            target_key = normalize_name(link)
            if target_key not in page_lookup:
                broken_links.append(f"{path.relative_to(ROOT)} -> [[{link}]]")

        if len(links) == 0:
            relative = str(path.relative_to(ROOT))
            if relative != "wiki/Home.md":
                orphan_pages.append(relative)

    relation_issues: list[str] = []
    for index, relation in enumerate(relation_rows, start=1):
        source_id = relation.get("source_id", "")
        target_id = relation.get("target_id", "")
        if source_id not in entity_lookup or target_id not in entity_lookup:
            relation_issues.append(
                f"Line {index} source_id={source_id} target_id={target_id} "
                f"relationship_type={relation.get('relationship_type', '')}"
            )

    risk_issues_no_control: list[str] = []
    risk_issues_no_event: list[str] = []
    for row in entity_rows:
        if row.get("type") != "RuiRo":
            continue
        risk_id = row.get("id")
        has_control = any(
            rel.get("relationship_type") == "MITIGATES" and rel.get("target_id") == risk_id
            for rel in relation_rows
        )
        has_event = any(
            rel.get("relationship_type") == "OBSERVED_AS" and rel.get("source_id") == risk_id
            for rel in relation_rows
        )
        if not has_control:
            risk_issues_no_control.append(f"{risk_id} (RuiRo không có KiemSoat)")
        if not has_event:
            risk_issues_no_event.append(f"{risk_id} (RuiRo không có SuKienRuiRo)")

    return (
        [str(p.relative_to(ROOT)) for p in wiki_files],
        all_wikilinks,
        broken_links,
        list(dict.fromkeys(entity_id_duplicates)),
        pages_not_in_entities,
        relation_issues,
        risk_issues_no_control,
        risk_issues_no_event,
        orphan_pages,
    )


def main() -> int:
    markdown_files, all_links, broken_links, duplicate_entity_ids, pages_not_in_entities, relation_issues, risk_issues_no_control, risk_issues_no_event, orphan_pages = validate()

    report_lines = [
        "# Wiki Validation Report",
        "",
        "## 1. Tổng số file Markdown",
        str(len(markdown_files)),
        "",
        "## 2. Tổng số wikilink",
        str(len(all_links)),
        "",
        "## 3. Wikilink trỏ tới trang không tồn tại",
    ]
    if broken_links:
        report_lines.extend(["- " + issue for issue in broken_links])
    else:
        report_lines.append("- Không có broken link.")

    report_lines.extend([
        "",
        "## 4. Entity bị trùng ID",
    ])
    if duplicate_entity_ids:
        report_lines.extend(["- " + item for item in duplicate_entity_ids])
    else:
        report_lines.append("- Không có duplicate ID.")

    report_lines.extend([
        "",
        "## 5. Trang có ID nhưng không tồn tại trong entities.csv",
    ])
    if pages_not_in_entities:
        report_lines.extend(["- " + item for item in pages_not_in_entities])
    else:
        report_lines.append("- Không có trang nào có ID không tồn tại trong entities.csv.")

    report_lines.extend([
        "",
        "## 6. Relation có source hoặc target không tồn tại",
    ])
    if relation_issues:
        report_lines.extend(["- " + item for item in relation_issues])
    else:
        report_lines.append("- Không có relation orphan.")

    report_lines.extend([
        "",
        "## 7. RuiRo không có KiemSoat",
    ])
    if risk_issues_no_control:
        report_lines.extend(["- " + item for item in risk_issues_no_control])
    else:
        report_lines.append("- Tất cả RuiRo đều có ít nhất 1 KiemSoat.")

    report_lines.extend([
        "",
        "## 8. RuiRo không có SuKienRuiRo",
    ])
    if risk_issues_no_event:
        report_lines.extend(["- " + item for item in risk_issues_no_event])
    else:
        report_lines.append("- Tất cả RuiRo đều có ít nhất 1 SuKienRuiRo.")

    report_lines.extend([
        "",
        "## 9. Trang không có liên kết với trang khác (orphan page)",
    ])
    if orphan_pages:
        report_lines.extend(["- " + item for item in orphan_pages])
    else:
        report_lines.append("- Không có orphan page.")

    report_text = "\n".join(report_lines) + "\n"
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print(report_text)

    has_issues = bool(broken_links or duplicate_entity_ids or pages_not_in_entities or relation_issues or risk_issues_no_control or risk_issues_no_event or orphan_pages)
    return 1 if has_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
