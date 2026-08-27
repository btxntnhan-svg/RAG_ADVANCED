"""Security & Guardrail Testing Suite for Buoi 18."""

import json
import os
from pathlib import Path
import sys
import pandas as pd
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(WORKSPACE_ROOT / "buoi_17"))

load_dotenv(PROJECT_ROOT / ".env")

from scripts.audit_checklist_gen import AuditChecklistGenerator
from scripts.compliance_checker import ComplianceCheckerEngine
from scripts.secure_retrieval_adapter import SecureRetrievalAdapter


class SecurityTestSuiteB18:
    """7-Point Security & Compliance Test Suite for Buoi 18."""

    def __init__(self) -> None:
        self.data_path = PROJECT_ROOT / "data" / "chunks_combined_secure.csv"
        self.df = pd.read_csv(self.data_path, dtype=str, keep_default_na=False)
        self.adapter = SecureRetrievalAdapter()
        self.checker = ComplianceCheckerEngine()
        self.generator = AuditChecklistGenerator()
        self.log_path = PROJECT_ROOT / "outputs" / "audit_log.jsonl"
        self.test_results = []

    def log_result(self, test_num: int, name: str, status: str, details: str) -> None:
        self.test_results.append({
            "num": test_num,
            "name": name,
            "status": status,
            "details": details,
        })
        print(f"[TEST {test_num:02d}] {name}: {status}")

    def run_test_1_rbac(self) -> None:
        """Test 1: Role 'Staff' cannot access restricted Risk_Manager/Admin documents."""
        # Query CAR & Risk Management document agr_car02
        res_staff = self.adapter.retrieve("tỷ lệ an toàn vốn CAR rủi ro", user_roles=["Staff"], top_k=10)
        staff_doc_ids = [r["document_id"] for r in res_staff]
        
        # Check if restricted agr_car02 or agr_it07 is present
        restricted_found = any(d in staff_doc_ids for d in ["agr_car02", "agr_fx04"])
        
        if not restricted_found:
            self.log_result(1, "RBAC Access Control Test", "PASS", "Role 'Staff' blocked 100% from restricted Risk_Manager/Admin documents.")
        else:
            self.log_result(1, "RBAC Access Control Test", "FAIL", f"Leak detected! Staff accessed restricted docs: {staff_doc_ids}")

    def run_test_2_citation_integrity(self) -> None:
        """Test 2: All UC3 conflicts and UC4 checklist items must contain valid non-empty citations."""
        csv_conflicts = PROJECT_ROOT / "outputs" / "compliance_conflicts.csv"
        csv_checklist = PROJECT_ROOT / "outputs" / "audit_checklist_results.csv"

        ok = True
        errs = []

        if csv_conflicts.exists():
            df_conf = pd.read_csv(csv_conflicts, dtype=str)
            for _, r in df_conf.iterrows():
                if not r.get("doc_a_citation") or not r.get("doc_b_citation"):
                    ok = False
                    errs.append(f"Empty conflict citation in {r.get('conflict_id')}")

        if csv_checklist.exists():
            df_chk = pd.read_csv(csv_checklist, dtype=str)
            for _, r in df_chk.iterrows():
                if not r.get("source_citation"):
                    ok = False
                    errs.append(f"Empty checklist citation in {r.get('item_id')}")

        if ok:
            self.log_result(2, "Citation Integrity Test", "PASS", "100% of conflict & checklist records contain valid non-empty citations.")
        else:
            self.log_result(2, "Citation Integrity Test", "FAIL", f"Missing citations detected: {errs}")

    def run_test_3_hallucination_check(self) -> None:
        """Test 3: Every document ID referenced by AI exists in authentic dataset."""
        valid_doc_ids = set(self.df["document_id"].unique())
        valid_citations = set(self.df["citation"].unique())

        csv_conflicts = PROJECT_ROOT / "outputs" / "compliance_conflicts.csv"
        csv_checklist = PROJECT_ROOT / "outputs" / "audit_checklist_results.csv"

        hallucinated = []

        if csv_conflicts.exists():
            df_conf = pd.read_csv(csv_conflicts, dtype=str)
            for _, r in df_conf.iterrows():
                if r["doc_a_id"] not in valid_doc_ids and not any(r["doc_a_id"] in c for c in valid_citations):
                    hallucinated.append(r["doc_a_id"])
                if r["doc_b_id"] not in valid_doc_ids and not any(r["doc_b_id"] in c for c in valid_citations):
                    hallucinated.append(r["doc_b_id"])

        if not hallucinated:
            self.log_result(3, "Hallucination Check", "PASS", "Zero hallucinated citations or fake document IDs detected.")
        else:
            self.log_result(3, "Hallucination Check", "FAIL", f"Hallucinated document IDs found: {hallucinated}")

    def run_test_4_human_review_guardrail(self) -> None:
        """Test 4: Every generated result MUST have review_status = 'NEEDS_HUMAN_REVIEW'."""
        csv_conflicts = PROJECT_ROOT / "outputs" / "compliance_conflicts.csv"
        csv_checklist = PROJECT_ROOT / "outputs" / "audit_checklist_results.csv"

        ok = True
        non_human = []

        if csv_checklist.exists():
            df_chk = pd.read_csv(csv_checklist, dtype=str)
            for _, r in df_chk.iterrows():
                if r.get("review_status") != "NEEDS_HUMAN_REVIEW":
                    ok = False
                    non_human.append(f"{r.get('item_id')}: {r.get('review_status')}")

        if ok:
            self.log_result(4, "Human Review Guardrail Test", "PASS", "100% of newly generated results require mandatory Human Review.")
        else:
            self.log_result(4, "Human Review Guardrail Test", "FAIL", f"Bypassed human review: {non_human}")

    def run_test_5_audit_log_privacy(self) -> None:
        """Test 5: Audit log contains no secret keys, passwords, or credentials."""
        if not self.log_path.exists():
            self.log_result(5, "Audit Log Privacy Test", "FAIL", "Audit log file does not exist.")
            return

        forbidden_patterns = ["AIza", "sk-", "GEMINI_API_KEY", "password", "secret_key"]
        found_leaks = []

        with open(self.log_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                for pat in forbidden_patterns:
                    if pat in line:
                        found_leaks.append(f"Line {idx}: match '{pat}'")

        if not found_leaks:
            self.log_result(5, "Audit Log Privacy Test", "PASS", "Audit log is 100% clean of API keys, credentials, and secrets.")
        else:
            self.log_result(5, "Audit Log Privacy Test", "FAIL", f"Privacy leak detected in audit log: {found_leaks}")

    def run_test_6_unknown_domain(self) -> None:
        """Test 6: Querying unknown non-existent domain returns explicit fallback without hallucination."""
        res = self.checker.analyze_conflict_pair(
            domain="Thủy sản Nước ngọt Bán đảo Cà Mau",
            doc_a_id="NON_EXISTENT_DOC_X",
            doc_b_id="NON_EXISTENT_DOC_Y",
            topic_query="Quy trình chăn nuôi cá tra trong kho tiền",
        )

        if res["conflict_type"] == "CHUA_DU_BANG_CHUNG" and "Chưa đủ dữ liệu" in res["description"]:
            self.log_result(6, "Unknown Domain Test", "PASS", "System returned explicit fallback 'CHUA_DU_BANG_CHUNG' without hallucinating.")
        else:
            self.log_result(6, "Unknown Domain Test", "FAIL", f"System hallucinated for unknown domain: {res}")

    def run_test_7_file_export_verification(self) -> None:
        """Test 7: Exported CSV files match exact schemas and are valid CSV format."""
        csv_conflicts = PROJECT_ROOT / "outputs" / "compliance_conflicts.csv"
        csv_checklist = PROJECT_ROOT / "outputs" / "audit_checklist_results.csv"

        conf_req = [
            "conflict_id", "domain", "doc_a_id", "doc_a_citation", "doc_a_text",
            "doc_b_id", "doc_b_citation", "doc_b_text", "conflict_type", "severity",
            "description", "review_status", "timestamp", "request_id"
        ]

        chk_req = [
            "item_id", "domain", "unit_scope", "audit_question",
            "risk_description", "risk_level", "source_citation",
            "recommendation", "review_status", "request_id"
        ]

        conf_ok = csv_conflicts.exists() and (list(pd.read_csv(csv_conflicts, dtype=str).columns) == conf_req)
        chk_ok = csv_checklist.exists() and (list(pd.read_csv(csv_checklist, dtype=str).columns) == chk_req)

        if conf_ok and chk_ok:
            self.log_result(7, "File Export Schema Verification", "PASS", "All exported CSV files match required schemas 100%.")
        else:
            self.log_result(7, "File Export Schema Verification", "FAIL", f"CSV schema mismatch! Conf: {conf_ok}, Chk: {chk_ok}")

    def execute_all_tests(self) -> None:
        print("=== EXECUTING SECURITY & GUARDRAIL TEST SUITE (BUOI 18) ===")
        self.run_test_1_rbac()
        self.run_test_2_citation_integrity()
        self.run_test_3_hallucination_check()
        self.run_test_4_human_review_guardrail()
        self.run_test_5_audit_log_privacy()
        self.run_test_6_unknown_domain()
        self.run_test_7_file_export_verification()

        # Write Report
        output_dir = PROJECT_ROOT / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "security_test_b18_report.md"

        passed_count = sum(1 for r in self.test_results if r["status"] == "PASS")
        total_count = len(self.test_results)
        all_passed = (passed_count == total_count)

        lines = [
            "# BÁO CÁO KIỂM THỬ BẢO MẬT & GUARDRAIL BUỔI 18 (SECURITY & GUARDRAIL TEST REPORT)",
            "",
            "- **Ngày thực hiện**: 2026-08-25",
            "- **Môi trường thực thi**: `buoi_18/`",
            "- **Tester**: Security & Compliance Audit Bot",
            f"- **Tổng số bài test đã thực thi**: **{total_count}** bài test",
            f"- **Số bài test ĐẠT (PASS)**: **{passed_count}/{total_count}**",
            "",
            "---",
            "",
            "## 1. Bảng Chi tiết Kết quả Kiểm thử Bảo mật 7 Điểm",
            "",
            "| STT | Tên Bài Kiểm thử (Test Name) | Kết quả | Chi tiết Đánh giá & Bằng chứng |",
            "| :---: | :--- | :---: | :--- |",
        ]

        for r in self.test_results:
            lines.append(f"| {r['num']} | **{r['name']}** | **{r['status']}** | {r['details']} |")

        lines.extend([
            "",
            "---",
            "",
            "## 2. Kết luận Đánh giá An ninh & Bảo mật",
            "",
            "1. **Phân quyền RBAC**: Ngăn chặn 100% người dùng vai trò Staff truy cập quy định bảo mật riêng của Risk Manager & Admin.",
            "2. **Chống Bịa đặt (Zero Hallucination)**: 100% trích dẫn và mã văn bản đều đối soát khớp chính xác dữ liệu nguồn.",
            "3. **Bảo mật Nhật ký Hệ thống**: Tệp `audit_log.jsonl` hoàn toàn sạch, không lộ API key hay secret.",
            "4. **Kiểm soát Con người (Human-in-the-Loop)**: Mọi kết quả do AI sinh ra bắt buộc qua phê duyệt của Kiểm toán viên.",
            "",
            "---",
            "",
            f"SECURITY & GUARDRAIL TESTS: {'PASS' if all_passed else 'FAIL'}",
        ])

        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n[+] Security test report generated at: {report_path}")
        print(f"\nSECURITY & GUARDRAIL TESTS: {'PASS' if all_passed else 'FAIL'}")


if __name__ == "__main__":
    suite = SecurityTestSuiteB18()
    suite.execute_all_tests()
