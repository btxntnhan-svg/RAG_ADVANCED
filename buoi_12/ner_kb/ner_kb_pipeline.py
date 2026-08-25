from __future__ import annotations

import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text


def clean_html_content(raw_html: Any) -> str:
    if pd.isna(raw_html):
        return ""
    soup = BeautifulSoup(str(raw_html), "html.parser")
    text = soup.get_text(" ", strip=True)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("•", " ")
    return text.strip()


def ensure_env_template() -> None:
    env_path = ROOT / ".env"
    example_path = ROOT / ".env.example"
    if not env_path.exists() and example_path.exists():
        env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")


def load_config() -> dict:
    ensure_env_template()
    load_dotenv(ROOT / ".env", override=False)
    return {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", "").strip(),
        "NEO4J_URI": os.getenv("NEO4J_URI", "bolt://localhost:7687").strip(),
        "NEO4J_USER": os.getenv("NEO4J_USER", "neo4j").strip(),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD", "").strip(),
        "NEO4J_DATABASE": os.getenv("NEO4J_DATABASE", "neo4j").strip(),
    }


def detect_data_quality(metadata: pd.DataFrame, content: pd.DataFrame):
    duplicate_ids = metadata["id"].duplicated().sum() + content["id"].duplicated().sum()
    mismatch_ids = len(set(metadata["id"]) - set(content["id"])) + len(set(content["id"]) - set(metadata["id"]))
    missing_values = metadata.isna().sum().sort_values(ascending=False).head(10).to_dict()
    return {
        "duplicate_ids": int(duplicate_ids),
        "mismatch_ids": int(mismatch_ids),
        "missing_values": missing_values,
    }


def build_cleaned_documents() -> pd.DataFrame:
    metadata = pd.read_csv(ROOT / "metadata.csv", dtype={"id": "string"})
    content = pd.read_csv(ROOT / "content.csv", dtype={"id": "string"})

    quality = detect_data_quality(metadata, content)
    merged = metadata.merge(content, on="id", how="inner", suffixes=("_meta", "_content"))
    merged["content_clean"] = merged["content_html"].apply(clean_html_content)
    merged = merged.sort_values("id").reset_index(drop=True)
    merged.to_csv(ROOT / "cleaned_documents.csv", index=False)

    print("BƯỚC 1: CLEANED_DOCUMENTS")
    print("documents=", len(merged))
    print("duplicate_ids=", quality["duplicate_ids"])
    print("id_mismatch=", quality["mismatch_ids"])
    print("missing_values=", quality["missing_values"])
    print("sample_cleaned=", merged[["id", "content_clean"]].head(2).to_dict(orient="records"))
    return merged


DOC_REF_RE = re.compile(
    r"\b(?:\d{1,4}/\d{4}/[A-Za-z0-9-]+|\d{1,4}/\d{4}/[A-Za-z0-9-]+(?:\s*[,;]\s*\d{1,4}/\d{4}/[A-Za-z0-9-]+)*)\b"
)


def extract_rule_candidates(cleaned: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()

    for _, row in cleaned.iterrows():
        source_id = str(row["id"])
        source_so = normalize_text(row.get("so_ky_hieu", ""))
        text = normalize_text(row.get("content_clean", ""))
        if not text:
            continue

        for trigger in ["Căn cứ", "Sửa đổi, bổ sung", "sửa đổi, bổ sung", "bãi bỏ", "thay thế", "thay thế bởi"]:
            for match in re.finditer(re.escape(trigger), text, flags=re.IGNORECASE):
                start = max(0, match.start() - 80)
                end = min(len(text), match.end() + 220)
                evidence = text[start:end]
                refs = DOC_REF_RE.findall(evidence)
                for target_so in refs:
                    target_so = target_so.strip()
                    if target_so == source_so:
                        continue
                    key = (source_id, source_so, target_so, trigger)
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append(
                        {
                            "source_id": source_id,
                            "source_so_ky_hieu": source_so,
                            "target_so_ky_hieu": target_so,
                            "trigger": trigger,
                            "evidence": evidence,
                        }
                    )

        for ref in DOC_REF_RE.findall(text):
            ref = ref.strip()
            if ref == source_so:
                continue
            key = (source_id, source_so, ref, "reference")
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "source_id": source_id,
                    "source_so_ky_hieu": source_so,
                    "target_so_ky_hieu": ref,
                    "trigger": "reference",
                    "evidence": text[:220],
                }
            )

    df = pd.DataFrame(rows, columns=["source_id", "source_so_ky_hieu", "target_so_ky_hieu", "trigger", "evidence"])
    df.to_csv(ROOT / "relation_candidates.csv", index=False)
    print("BƯỚC 2: RELATION_CANDIDATES")
    print("total_candidates=", len(df))
    print(df["trigger"].value_counts().to_dict())
    print(df.head(10).to_dict(orient="records"))
    return df


def heuristic_entity_extraction(content: str, doc_row: pd.Series) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    doc_id = str(doc_row.get("id", ""))

    raw_fields = {
        "CoQuan": [doc_row.get("co_quan_ban_hanh", ""), doc_row.get("nganh", "")],
        "NguoiKy": [doc_row.get("nguoi_ky", "")],
        "DoiTuongApDung": [doc_row.get("pham_vi", ""), doc_row.get("thong_tin_ap_dung", ""), "Tổ chức tín dụng", "Chi nhánh ngân hàng nước ngoài", "Quỹ tín dụng nhân dân"],
        "LinhVuc": [doc_row.get("linh_vuc", ""), doc_row.get("nganh", "")],
    }

    for entity_type, values in raw_fields.items():
        for value in values:
            cleaned = normalize_text(value)
            if not cleaned or cleaned.lower() in {"nan", "chưa phân loại", "chưa xác định"}:
                continue
            evidence = content[:220] if content else cleaned
            entities.append(
                {
                    "entity": cleaned,
                    "entity_type": entity_type,
                    "source": "content_clean",
                    "method": "heuristic",
                    "confidence": 0.75 if entity_type in {"CoQuan", "NguoiKy"} else 0.7,
                    "evidence": evidence,
                    "document_id": doc_id,
                }
            )

    for label in ["Ngân hàng Nhà nước Việt Nam", "Bộ Tài chính", "Chính phủ", "Quốc hội"]:
        if label.lower() in content.lower() and not any(item["entity"] == label for item in entities):
            entities.append(
                {
                    "entity": label,
                    "entity_type": "CoQuan",
                    "source": "content_clean",
                    "method": "heuristic",
                    "confidence": 0.8,
                    "evidence": content[:220],
                    "document_id": doc_id,
                }
            )

    return entities


def build_entity_outputs(cleaned: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    extracted_rows: list[dict[str, Any]] = []
    enriched_rows: list[dict[str, Any]] = []

    for _, row in cleaned.iterrows():
        content = normalize_text(row.get("content_clean", ""))
        extracted_rows.extend(heuristic_entity_extraction(content, row))

        enriched = row.to_dict()
        enriched["co_quan_enriched"] = row.get("co_quan_ban_hanh", "")
        enriched["nguoi_ky_enriched"] = row.get("nguoi_ky", "")
        enriched["doi_tuong_ap_dung_enriched"] = row.get("pham_vi", "") or "Tổ chức tín dụng"
        enriched["linh_vuc_enriched"] = row.get("linh_vuc", "") or row.get("nganh", "") or "Chưa phân loại"
        enriched_rows.append(enriched)

    extracted_df = pd.DataFrame(extracted_rows)
    if not extracted_df.empty:
        extracted_df = extracted_df[["document_id", "entity", "entity_type", "source", "method", "confidence", "evidence"]]
    enriched_df = pd.DataFrame(enriched_rows)

    extracted_df.to_csv(ROOT / "extracted_entities_raw.csv", index=False)
    enriched_df.to_csv(ROOT / "enriched_metadata.csv", index=False)

    print("BƯỚC 3: ENTITY_EXTRACTION")
    print("documents_success=", len(cleaned))
    print("documents_failed=", 0)
    print("entity_counts=", extracted_df["entity_type"].value_counts().to_dict() if not extracted_df.empty else {})
    print(extracted_df.head(5).to_dict(orient="records"))
    return extracted_df, enriched_df


def normalize_entity_name(name: str) -> str:
    text = unicodedata.normalize("NFKC", name or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def alias_map(name: str) -> str:
    normalized = normalize_entity_name(name).lower()
    aliases = {
        "nhnn": "Ngân hàng Nhà nước Việt Nam",
        "ngan hang nha nuoc viet nam": "Ngân hàng Nhà nước Việt Nam",
        "ngan hang nha nuoc": "Ngân hàng Nhà nước Việt Nam",
        "bo tai chinh": "Bộ Tài chính",
        "chinh phu": "Chính phủ",
        "quoc hoi": "Quốc hội",
        "to chuc tin dung": "Tổ chức tín dụng",
        "chi nhanh ngan hang nuoc ngoai": "Chi nhánh ngân hàng nước ngoài",
        "quy tin dung nhan dan": "Quỹ tín dụng nhân dân",
    }
    return aliases.get(normalized, normalize_entity_name(name))


def build_entities(extracted: pd.DataFrame) -> pd.DataFrame:
    if extracted.empty:
        empty = pd.DataFrame(columns=["entity_id", "entity_type", "canonical_name", "original_name", "source_doc_id", "method", "confidence", "evidence"])
        empty.to_csv(ROOT / "entities.csv", index=False)
        return empty

    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for _, row in extracted.iterrows():
        entity = normalize_entity_name(str(row["entity"]))
        canonical = alias_map(entity)
        key = (row["entity_type"], canonical)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "entity_id": f"{row['entity_type']}-{len(rows) + 1}",
                "entity_type": row["entity_type"],
                "canonical_name": canonical,
                "original_name": entity,
                "source_doc_id": str(row.get("document_id", "")),
                "method": row.get("method", "heuristic"),
                "confidence": float(row.get("confidence", 0.0) or 0.0),
                "evidence": row.get("evidence", ""),
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "entities.csv", index=False)
    print("BƯỚC 4: ENTITIES")
    print("before=", len(extracted))
    print("after=", len(out))
    print(out.head(10).to_dict(orient="records"))
    return out


def build_relationships_raw(cleaned: pd.DataFrame, candidates: pd.DataFrame, entities: pd.DataFrame, enriched: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    doc_lookup = set(cleaned["id"].astype(str))

    for _, row in candidates.iterrows():
        source_id = str(row["source_id"])
        target_code = str(row["target_so_ky_hieu"])
        trigger = str(row["trigger"]).lower()
        evidence = str(row["evidence"])
        if source_id not in doc_lookup:
            continue

        rel_type = "THAM_CHIEU"
        if "sửa đổi" in trigger or "bo sung" in trigger:
            rel_type = "SUA_DOI_BO_SUNG"
        elif "thay thế" in trigger:
            rel_type = "THAY_THE_BOI"

        rows.append(
            {
                "source": source_id,
                "target": target_code,
                "relationship_type": rel_type,
                "method": "rule",
                "confidence": 0.8,
                "evidence": evidence,
            }
        )

    for _, doc in cleaned.iterrows():
        doc_id = str(doc["id"])
        doc_co_quan = normalize_text(doc.get("co_quan_ban_hanh", ""))
        if doc_co_quan:
            rows.append({"source": doc_id, "target": alias_map(doc_co_quan), "relationship_type": "BAN_HANH_BOI", "method": "metadata", "confidence": 0.85, "evidence": doc_co_quan})

        doc_nguoi_ky = normalize_text(doc.get("nguoi_ky", ""))
        if doc_nguoi_ky:
            rows.append({"source": doc_id, "target": doc_nguoi_ky, "relationship_type": "KY_BOI", "method": "metadata", "confidence": 0.85, "evidence": doc_nguoi_ky})

        doc_linh_vuc = normalize_text(doc.get("linh_vuc", ""))
        if doc_linh_vuc:
            rows.append({"source": doc_id, "target": doc_linh_vuc, "relationship_type": "THUOC_LINH_VUC", "method": "metadata", "confidence": 0.82, "evidence": doc_linh_vuc})

        doc_targets = normalize_text(doc.get("pham_vi", ""))
        if doc_targets:
            rows.append({"source": doc_id, "target": doc_targets, "relationship_type": "AP_DUNG_CHO", "method": "metadata", "confidence": 0.72, "evidence": doc_targets})

    raw = pd.DataFrame(rows)
    raw = raw.drop_duplicates(subset=["source", "target", "relationship_type", "evidence"], keep="first").reset_index(drop=True)
    raw.to_csv(ROOT / "relationships_raw.csv", index=False)
    print("BƯỚC 5: RELATIONSHIPS_RAW")
    print(raw["relationship_type"].value_counts().to_dict())
    print(raw.head(10).to_dict(orient="records"))
    return raw


def validate_relationships(raw: pd.DataFrame, cleaned: pd.DataFrame, entities: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    valid_types = {"THAM_CHIEU", "SUA_DOI_BO_SUNG", "THAY_THE_BOI", "BAN_HANH_BOI", "KY_BOI", "AP_DUNG_CHO", "THUOC_LINH_VUC"}
    doc_lookup = set(cleaned["id"].astype(str))
    entity_lookup = set(entities["canonical_name"])
    valid_rows = []
    invalid_rows = []

    for _, row in raw.iterrows():
        source = str(row.get("source", ""))
        target = str(row.get("target", ""))
        rel_type = str(row.get("relationship_type", ""))
        evidence = normalize_text(row.get("evidence", ""))
        reason = []

        if not source or not target or not rel_type:
            reason.append("missing_field")
        if rel_type not in valid_types:
            reason.append("invalid_type")
        if not evidence:
            reason.append("missing_evidence")
        if source == target:
            reason.append("self_loop")

        if rel_type in {"THAM_CHIEU", "SUA_DOI_BO_SUNG", "THAY_THE_BOI"}:
            if source not in doc_lookup or target not in doc_lookup:
                reason.append("invalid_document_target")
        elif rel_type in {"BAN_HANH_BOI", "KY_BOI", "AP_DUNG_CHO", "THUOC_LINH_VUC"}:
            if source not in doc_lookup:
                reason.append("invalid_document_source")
            if target not in entity_lookup and not any(str(entity) in target for entity in entity_lookup):
                reason.append("invalid_entity_target")

        if reason:
            invalid_rows.append({**row.to_dict(), "rejection_reason": ";".join(reason)})
        else:
            valid_rows.append(row.to_dict())

    valid_df = pd.DataFrame(valid_rows)
    invalid_df = pd.DataFrame(invalid_rows)
    valid_df.to_csv(ROOT / "relationships.csv", index=False)
    invalid_df.to_csv(ROOT / "validation_report.csv", index=False)

    print("BƯỚC 6: VALIDATION")
    print("raw=", len(raw))
    print("valid=", len(valid_df))
    print("invalid=", len(invalid_df))
    print("invalid_summary=", invalid_df["rejection_reason"].value_counts().head().to_dict())
    return valid_df, invalid_df


def neo4j_check() -> dict:
    config = load_config()
    uri = config["NEO4J_URI"]
    user = config["NEO4J_USER"]
    pw = config["NEO4J_PASSWORD"]
    database = config["NEO4J_DATABASE"]
    result = {
        "configured": bool(uri and user and pw),
        "uri": uri,
        "user": user,
        "database": database,
        "status": "FAIL",
        "details": "No Neo4j credentials configured.",
    }

    try:
        from neo4j import GraphDatabase

        if not pw or pw == "YOUR_NEO4J_PASSWORD":
            result["details"] = "Neo4j password missing or placeholder."
            return result

        driver = GraphDatabase.driver(uri, auth=(user, pw), database=database)
        with driver.session(database=database) as session:
            session.run("RETURN 1 AS ok")
        result["status"] = "PASS"
        result["details"] = "Connection verified."
        driver.close()
    except Exception as exc:  # pragma: no cover
        result["details"] = str(exc)
    return result


def import_knowledge_graph() -> dict:
    config = load_config()
    uri = config["NEO4J_URI"]
    user = config["NEO4J_USER"]
    pw = config["NEO4J_PASSWORD"]
    database = config["NEO4J_DATABASE"]

    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(uri, auth=(user, pw))
        with driver.session(database=database) as session:
            session.run("CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE")
            session.run("CREATE CONSTRAINT coquan_name IF NOT EXISTS FOR (n:CoQuan) REQUIRE n.name IS UNIQUE")
            session.run("CREATE CONSTRAINT nguoiKy_name IF NOT EXISTS FOR (n:NguoiKy) REQUIRE n.name IS UNIQUE")
            session.run("CREATE CONSTRAINT doituong_name IF NOT EXISTS FOR (n:DoiTuongApDung) REQUIRE n.name IS UNIQUE")
            session.run("CREATE CONSTRAINT linhvuc_name IF NOT EXISTS FOR (n:LinhVuc) REQUIRE n.name IS UNIQUE")

            docs = pd.read_csv(ROOT / "cleaned_documents.csv")
            for _, row in docs.iterrows():
                doc_id = str(row["id"])
                session.run(
                    "MERGE (d:Document {id: $id}) SET d.so_ky_hieu = $so_ky_hieu, d.title = $title",
                    id=doc_id,
                    so_ky_hieu=str(row.get("so_ky_hieu", "")),
                    title=str(row.get("title", "")),
                )

            entities = pd.read_csv(ROOT / "entities.csv")
            entity_labels = {
                "CoQuan": "CoQuan",
                "NguoiKy": "NguoiKy",
                "DoiTuongApDung": "DoiTuongApDung",
                "LinhVuc": "LinhVuc",
            }
            for _, entity in entities.iterrows():
                label = entity_labels.get(str(entity.get("entity_type", "")), "Entity")
                name = str(entity.get("canonical_name", ""))
                if not name:
                    continue
                session.run(
                    f"MERGE (n:{label} {{name: $name}}) SET n.entity_id = $entity_id, n.entity_type = $entity_type, n.original_name = $original_name",
                    name=name,
                    entity_id=str(entity.get("entity_id", "")),
                    entity_type=str(entity.get("entity_type", "")),
                    original_name=str(entity.get("original_name", "")),
                )

            rels = pd.read_csv(ROOT / "relationships.csv")
            rel_type_map = {
                "BAN_HANH_BOI": "CoQuan",
                "KY_BOI": "NguoiKy",
                "AP_DUNG_CHO": "DoiTuongApDung",
                "THUOC_LINH_VUC": "LinhVuc",
            }
            for _, rel in rels.iterrows():
                source = str(rel.get("source", ""))
                target = str(rel.get("target", ""))
                rel_type = str(rel.get("relationship_type", ""))
                if rel_type in {"THAM_CHIEU", "SUA_DOI_BO_SUNG", "THAY_THE_BOI"}:
                    session.run(
                        f"MATCH (a:Document {{id: $source}}), (b:Document {{so_ky_hieu: $target}}) MERGE (a)-[r:{rel_type}]->(b)",
                        source=source,
                        target=target,
                    )
                elif rel_type in rel_type_map:
                    label = rel_type_map[rel_type]
                    session.run(
                        f"MATCH (d:Document {{id: $source}}), (n:{label} {{name: $target}}) MERGE (d)-[r:{rel_type}]->(n)",
                        source=source,
                        target=target,
                    )

            counts = {
                "nodes": session.run("MATCH (n) RETURN count(n) AS total").single()["total"],
                "relationships": session.run("MATCH ()-[r]->() RETURN count(r) AS total").single()["total"],
            }
            node_counts = list(session.run("MATCH (n) RETURN labels(n) AS labels, count(*) AS total ORDER BY total DESC"))
            edge_counts = list(session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS total ORDER BY total DESC"))
            driver.close()
            return {
                "status": "PASS",
                "database": database,
                "counts": counts,
                "node_counts": [dict(x) for x in node_counts],
                "edge_counts": [dict(x) for x in edge_counts],
            }
    except Exception as exc:  # pragma: no cover
        return {
            "status": "FAIL",
            "error": str(exc),
            "database": database,
        }


def main() -> None:
    config = load_config()
    print("ENV", {k: v for k, v in config.items() if "KEY" not in k and "PASSWORD" not in k})
    cleaned = build_cleaned_documents()
    candidates = extract_rule_candidates(cleaned)
    extracted, enriched = build_entity_outputs(cleaned)
    entities = build_entities(extracted)
    relationships_raw = build_relationships_raw(cleaned, candidates, entities, enriched)
    valid, invalid = validate_relationships(relationships_raw, cleaned, entities)
    neo = neo4j_check()
    print("BƯỚC 7: NEO4J_CHECK")
    print(neo)
    if neo.get("status") == "PASS":
        result = import_knowledge_graph()
        print("BƯỚC 8: IMPORT")
        print(result)
        print("BƯỚC 9: SAMPLE")
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(config["NEO4J_URI"], auth=(config["NEO4J_USER"], config["NEO4J_PASSWORD"]))
            with driver.session(database=config["NEO4J_DATABASE"]) as session:
                doc_entity = session.run("MATCH (d:Document)-[:KY_BOI]->(p:NguoiKy) RETURN d.id AS doc_id, p.name AS signer LIMIT 5").data()
                doc_apdung = session.run("MATCH (d:Document)-[:AP_DUNG_CHO]->(o:DoiTuongApDung) RETURN d.id AS doc_id, o.name AS target LIMIT 5").data()
                doc_doc = session.run("MATCH (a:Document)-[r]->(b:Document) WHERE type(r) IN ['THAM_CHIEU', 'SUA_DOI_BO_SUNG', 'THAY_THE_BOI'] RETURN a.id AS src, b.id AS dst, type(r) AS rel LIMIT 5").data()
            driver.close()
            print({"ky_boi": doc_entity, "ap_dung": doc_apdung, "doc_doc": doc_doc})
        except Exception as exc:  # pragma: no cover
            print({"sample_query_error": str(exc)})
    print("FINISHED: created outputs in", ROOT)


if __name__ == "__main__":
    main()
