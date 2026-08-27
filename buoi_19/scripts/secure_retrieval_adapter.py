"""Secure Retrieval Adapter for Buoi 17.

Wraps existing SecureRetriever (from Buoi 14/16) without modifying original retriever code,
standardizing candidate output dictionaries to match Buoi 17 interface specifications.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(WORKSPACE_ROOT / "buoi_14"))

from src.secure_retriever import SecureRetriever, load_secure_corpus


class SecureRetrievalAdapter:
    """Adapter wrapping SecureRetriever to standardize output keys for Buoi 17."""

    def __init__(self, retriever: SecureRetriever | None = None) -> None:
        self.retriever = retriever or SecureRetriever()

    def retrieve(
        self,
        query: str,
        user_roles: list[str] | tuple[str, ...],
        method: str = "bm25",
        top_k: int = 5,
        candidate_k: int = 20,
    ) -> list[dict[str, Any]]:
        raw_results = self.retriever.retrieve(
            query=query,
            user_roles=user_roles,
            method=method,
            top_k=top_k,
            candidate_k=candidate_k,
        )

        standardized: list[dict[str, Any]] = []
        for idx, item in enumerate(raw_results, 1):
            chunk_id = str(item.get("chunk_id", ""))
            doc_id = str(item.get("document_id", ""))
            citation = str(item.get("citation", ""))
            
            # Lookup original title/citation_code from loaded rows if missing
            row_meta = next((r for r in self.retriever.rows if r.get("chunk_id") == chunk_id), {})
            title = str(row_meta.get("title", doc_id))
            article = str(row_meta.get("citation_code", citation))

            std_item = {
                "rank": item.get("rank", idx),
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "title": title,
                "article": article,
                "citation": citation,
                "allowed_roles": list(item.get("allowed_roles", [])),
                "access_decision": "ALLOWED",
                "retrieval_method": str(item.get("retrieval_method", method)),
                "text": str(item.get("text", "")),
                "score": float(item.get("score", 0.0)),
            }
            standardized.append(std_item)

        return standardized
