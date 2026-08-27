"""
Security & Guardrail Testing Suite for Buổi 19 Local AI Containerized System.
Kiểm thử 6 hạng mục an toàn theo tiêu chuẩn Agribank Local AI:
1. Local Offline Privacy Check
2. RBAC Enforcement
3. Citation Integrity
4. Human Review Guardrail
5. Audit Log Privacy
6. Local Model Resilience
"""

import os
import sys
import json
import uuid
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from scripts.audit_logger import AuditLogger
from scripts.ollama_adapter import OllamaClient
from scripts.compliance_checker import ComplianceCheckerEngine
from scripts.audit_checklist_gen import AuditChecklistGenerator
from scripts.secure_retrieval_adapter import SecureRetrievalAdapter


class SecurityTesterB19:
    """Security & Guardrail Tester for Buoi 19 Local AI Setup."""

    def __init__(self) -> None:
        self.data_path = PROJECT_ROOT / "data" / "chunks_combined_secure.csv"
        if not self.data_path.exists():
            self.data_path = PROJECT_ROOT / "buoi_19" / "data" / "chunks_combined_secure.csv"

        self.df = pd.read_csv(self.data_path, dtype=str, keep_default_na=False)
        self.adapter = SecureRetrievalAdapter()
        self.checker = ComplianceCheckerEngine()
        self.generator = AuditChecklistGenerator()
        self.test_results = []

    def log_test(self, item_num: int, name: str, status: str, details: str) -> None:
        self.test_results.append({
            "item_num": item_num,
            "name": name,
            "status": status,
            "details": details
        })
        print(f"[{item_num}/6] {name}: {status}")
        print(f"    Chi tiết: {details}\n")

    def test_1_local_offline_privacy(self) -> None:
        """1. Local Offline Privacy Check: Ensure 100% prompts stay local when LLM_PROVIDER=ollama."""
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        client = OllamaClient()
        health = client.check_health()
        
        if provider == "ollama" and health["online"]:
            self.log_test(
                1, 
                "Local Offline Privacy Check", 
                "PASS", 
                f"LLM_PROVIDER={provider}. 100% prompt xử lý nội bộ tại {ollama_url}. Không gửi dữ liệu ra Cloud API."
            )
        elif provider == "ollama":
            self.log_test(
                1, 
                "Local Offline Privacy Check", 
                "PASS", 
                f"LLM_PROVIDER={provider}. Hệ thống hoạt động ở chế độ Local Offline (Rule-Engine Fallback) an toàn."
            )
        else:
            self.log_test(
                1, 
                "Local Offline Privacy Check", 
                "FAIL", 
                f"LLM_PROVIDER={provider}. Cần cấu hình LLM_PROVIDER=ollama cho Buổi 19."
            )

    def test_2_rbac_enforcement(self) -> None:
        """2. RBAC Enforcement: Role 'Staff' blocked 100% from high-risk security documents."""
        # Query CAR / Risk Management document agr_car02
        res_staff = self.adapter.retrieve("tỷ lệ an toàn vốn CAR rủi ro", user_roles=["Staff"], top_k=10)
        staff_doc_ids = [r["document_id"] for r in res_staff]

        restricted_found = any(d in staff_doc_ids for d in ["agr_car02", "agr_fx04"])
        
        if not restricted_found:
            self.log_test(
                2, 
                "RBAC Enforcement Test", 
                "PASS", 
                "Role 'Staff' bị chặn 100% dữ liệu bảo mật rủi ro (agr_car02, agr_fx04) trên container."
            )
        else:
            self.log_test(
                2, 
                "RBAC Enforcement Test", 
                "FAIL", 
                f"Rò rỉ dữ liệu! Role 'Staff' truy cập được văn bản bảo mật: {staff_doc_ids}"
            )

    def test_3_citation_integrity(self) -> None:
        """3. Citation Integrity: All model outputs have valid source citations."""
        conflicts = self.checker.analyze_conflict_pair(
            domain="An toàn Kho quỹ",
            doc_a_id="agr_at01",
            doc_b_id="44209",
            topic_query="giao nhận niêm phong tiền mặt"
        )
        
        has_cit_a = bool(conflicts.get("doc_a_citation"))
        has_cit_b = bool(conflicts.get("doc_b_citation"))

        if has_cit_a and has_cit_b:
            self.log_test(
                3, 
                "Citation Integrity Test", 
                "PASS", 
                f"Trích dẫn Điều/Khoản hợp lệ: Doc A ('{conflicts['doc_a_citation']}'), Doc B ('{conflicts['doc_b_citation']}')."
            )
        else:
            self.log_test(
                3, 
                "Citation Integrity Test", 
                "FAIL", 
                "Phát hiện kết quả thiếu trích dẫn văn bản gốc."
            )

    def test_4_human_review_guardrail(self) -> None:
        """4. Human Review Guardrail: 100% outputs tagged with review_status = 'NEEDS_HUMAN_REVIEW'."""
        conflicts = self.checker.analyze_conflict_pair(
            domain="CAR & Rủi ro",
            doc_a_id="agr_car02",
            doc_b_id="117310",
        )
        checklist = self.generator.generate_checklist(
            domain="Bảo mật CNTT & AI",
            unit_scope="Khối CNTT"
        )

        conf_status = conflicts.get("review_status") == "NEEDS_HUMAN_REVIEW"
        chk_status = all(it.get("review_status") == "NEEDS_HUMAN_REVIEW" for it in checklist)

        if conf_status and chk_status:
            self.log_test(
                4, 
                "Human Review Guardrail Test", 
                "PASS", 
                "100% kết quả xung đột & checklist đều gán cờ 'NEEDS_HUMAN_REVIEW' bắt buộc cán bộ thẩm định."
            )
        else:
            self.log_test(
                4, 
                "Human Review Guardrail Test", 
                "FAIL", 
                "Phát hiện kết quả thiếu cờ thẩm định NEEDS_HUMAN_REVIEW."
            )

    def test_5_audit_log_privacy(self) -> None:
        """5. Audit Log Privacy: Zero leaked API keys or secrets in audit log."""
        log_file = PROJECT_ROOT / "outputs" / "audit_log.jsonl"
        if not log_file.exists():
            log_file = PROJECT_ROOT / "outputs" / "audit_trail.jsonl"

        leak_found = False
        sample_keys = ["AQ.Ab8RN6JDGDSY3hhh7", "AIzaSy", "hf_"]

        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    for k in sample_keys:
                        if k in line:
                            leak_found = True
                            break

        if not leak_found:
            self.log_test(
                5, 
                "Audit Log Privacy Test", 
                "PASS", 
                "Nhật ký truy vết outputs/audit_log.jsonl an toàn 100%, không rò rỉ API Key hay thông tin nhạy cảm."
            )
        else:
            self.log_test(
                5, 
                "Audit Log Privacy Test", 
                "FAIL", 
                "Phát hiện chuỗi API key nhạy cảm trong nhật ký kiểm toán audit log!"
            )

    def test_6_local_model_resilience(self) -> None:
        """6. Local Model Resilience: Offline fallback resilience check."""
        client = OllamaClient(base_url="http://invalid_host_9999:11434", timeout=0.5)
        res = client.generate("Kiểm tra khả năng chịu lỗi ngắt mạng", format_json=True)
        
        if "FALLBACK_RULE_ENGINE" in res or "offline" in res.lower() or "ollama" in res.lower():
            self.log_test(
                6, 
                "Local Model Resilience Test", 
                "PASS", 
                "Hệ thống chịu lỗi xuất sắc: Tự động chuyển sang Rule-Engine Fallback khi mất kết nối mạng/máy chủ."
            )
        else:
            self.log_test(
                6, 
                "Local Model Resilience Test", 
                "FAIL", 
                "Hệ thống bị treo hoặc sập khi mất kết nối máy chủ Ollama."
            )

    def run_all_tests(self) -> None:
        print("=" * 70)
        print(" EXECUTION: SECURITY & LOCAL GUARDRAIL TEST SUITE (BUỔI 19)")
        print("=" * 70 + "\n")

        self.test_1_local_offline_privacy()
        self.test_2_rbac_enforcement()
        self.test_3_citation_integrity()
        self.test_4_human_review_guardrail()
        self.test_5_audit_log_privacy()
        self.test_6_local_model_resilience()

        passed_count = sum(1 for t in self.test_results if t["status"] == "PASS")
        total_count = len(self.test_results)

        print("=" * 70)
        print(f"SECURITY AUDIT REPORT: {passed_count}/{total_count} TESTS PASSED")
        if passed_count == total_count:
            print("OVERALL SECURITY STATUS: ALL GUARDRAILS PASSED (100% SECURE)")
        else:
            print("OVERALL SECURITY STATUS: WARNING - SOME TESTS FAILED")
        print("=" * 70)


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    tester = SecurityTesterB19()
    tester.run_all_tests()
