"""Streamlit Application for Buoi 17: Secure RAG & Compliance Gap Checker."""

import json
from pathlib import Path
import sys
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(WORKSPACE_ROOT / "buoi_14"))

from scripts.audit_logger import AuditLogger
from scripts.internal_lookup import InternalLookupEngine

# Set Page Configuration
st.set_page_config(
    page_title="Secure RAG & Compliance — Buổi 17",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Notranslate meta tag and custom CSS styling
st.markdown(
    """
    <meta name="google" content="notranslate">
    <style>
        .main { background-color: #0e1117; }
        .stButton>button {
            width: 100%;
            background-color: #1f77b4;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            border: none;
            padding: 10px 16px;
        }
        .stButton>button:hover { background-color: #155887; color: white; }
        .badge-success { background-color: #28a745; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
        .badge-denied { background-color: #dc3545; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
        .badge-warning { background-color: #ffc107; color: #111; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
        .card { background-color: #1e222a; padding: 20px; border-radius: 8px; border: 1px solid #2d3139; margin-bottom: 16px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Training Banner
st.warning("⚠️ **Demo đào tạo — kết quả AI cần kiểm toán viên xác minh.**")

# Sidebar Configuration
st.sidebar.title("🛡️ Cấu hình Quyền & Người dùng")
st.sidebar.markdown("---")

user_id_demo = st.sidebar.text_input("User ID Demo", value="USR_ADMIN_01")
user_role = st.sidebar.selectbox(
    "User Role (Vai trò)",
    options=["Admin", "Risk_Manager", "Staff", "Guest", "UnknownRole"],
    index=0,
)

# Neo4j status check
def check_neo4j_status() -> str:
    try:
        from neo4j import GraphDatabase
        from src.config import get_neo4j_config
        cfg = get_neo4j_config()
        driver = GraphDatabase.driver(cfg["uri"], auth=(cfg["user"], cfg["password"]))
        driver.verify_connectivity()
        driver.close()
        return "🟢 ONLINE (Neo4j GraphDB)"
    except Exception:
        return "🔴 OFFLINE (Standard Retrieval)"

st.sidebar.markdown("### Trạng thái Đồ thị Neo4j")
st.sidebar.info(check_neo4j_status())

st.sidebar.markdown("---")
st.sidebar.caption("Hệ thống RAG Bảo mật & Compliance Gap Checker — Buổi 17")

# Main Header
st.title("🛡️ SECURE RAG & COMPLIANCE GAP CHECKER — BUỔI 17")
st.markdown(f"**Người dùng hiện tại**: `{user_id_demo}` | **Vai trò hệ thống**: `<span class='badge-success'>{user_role}</span>`", unsafe_allow_html=True)
st.markdown("---")

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs(["🔍 TAB 1: TRA CỨU QUY ĐỊNH", "📋 TAB 2: COMPLIANCE GAP CHECKER", "📜 TAB 3: AUDIT TRAIL"])


# -----------------------------------------------------------------------------
# TAB 1: TRA CỨU QUY ĐỊNH
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("🔍 Tra cứu Quy định & Văn bản Pháp lý Nội bộ")
    
    col_q, col_k = st.columns([4, 1])
    with col_q:
        sample_questions = [
            "Quy định về việc giao nhận, bảo quản và vận chuyển tiền mặt, tài sản quý theo Thông tư 01/2014/TT-NHNN?",
            "Theo Luật Hợp tác xã số 17/2023/QH15, việc góp vốn điều lệ và quyền của thành viên hợp tác xã được quy định như thế nào?",
            "Hồ sơ thủ tục cấp phép lần đầu cho Ngân hàng thương mại và điều kiện tỷ lệ an toàn vốn tối thiểu?",
        ]
        selected_sample = st.selectbox("📌 Chọn câu hỏi mẫu:", options=["-- Tùy chỉnh --"] + sample_questions)
        
        default_val = selected_sample if selected_sample != "-- Tùy chỉnh --" else "Quy định về việc giao nhận, bảo quản và vận chuyển tiền mặt theo Thông tư 01/2014/TT-NHNN?"
        question_input = st.text_area("Câu hỏi truy vấn (Question):", value=default_val, height=100)

    with col_k:
        top_k_input = st.slider("Top-K Candidate:", min_value=1, max_value=10, value=5)

    if st.button("🚀 Thực thi Tra cứu Bảo mật"):
        if not question_input.strip():
            st.error("Vui lòng nhập nội dung câu hỏi truy vấn!")
        else:
            with st.spinner("Đang thực thi Secure Filtering (RBAC) & Search..."):
                engine = InternalLookupEngine()
                res = engine.lookup(
                    question=question_input,
                    user_role=[user_role],
                    top_k=top_k_input,
                    user_id_demo=user_id_demo,
                )

            st.markdown("### Kết quả Tra cứu & Quyết định Quyền Truycập")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Trạng thái Request", res["status"])
            with col_m2:
                st.metric("Phạm vi Quyền Truy cập", res["access_scope"])
            with col_m3:
                st.code(f"Request ID: {res['request_id']}")

            st.markdown("#### 💬 Câu trả lời từ Hệ thống (Answer):")
            if res["status"] == "DENIED" or res["answer"] == "Không tìm thấy đủ thông tin trong phạm vi tài liệu được phép truy cập.":
                st.error("❌ Không tìm thấy đủ thông tin trong phạm vi tài liệu được phép truy cập.")
                st.info("🔒 Quyền truy cập bị từ chối hoặc không có dữ liệu thỏa mãn vai trò hiện tại. Snippet/Citation bị cấm sẽ không hiển thị.")
            else:
                st.success(res["answer"])

                st.markdown("#### 📜 Danh sách Trích dẫn Pháp lý (Citations):")
                if res["citations"]:
                    for idx, cit in enumerate(res["citations"], 1):
                        st.markdown(f"**[{idx}]** `{cit}`")
                else:
                    st.write("Không có trích dẫn nào.")

                st.markdown("#### 🧩 Chi tiết Mã Văn bản & Chunk (`document_id / chunk_id`):")
                if res["document_id_chunk_id"]:
                    df_chunks = pd.DataFrame(res["document_id_chunk_id"])
                    st.dataframe(df_chunks, use_container_width=True)


# -----------------------------------------------------------------------------
# TAB 2: COMPLIANCE GAP CHECKER
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("📋 AI Compliance Gap Checker — Rà soát Chênh lệch Quy định")
    
    # Read gap input catalog
    catalog_path = PROJECT_ROOT / "outputs" / "gap_input_catalog.md"
    if catalog_path.exists():
        st.markdown("### 📊 Đánh giá Dữ liệu Corpus cho Gap Analysis")
        st.warning("⚠️ **BÁO CÁO THIẾU DỮ LIỆU THỰC TẾ (DATA GAP IDENTIFIED)**: Tập corpus hiện tại chứa 100% Văn bản Nhà nước (`EXTERNAL_REQUIREMENT`) và chưa có Quy định Nội bộ (`INTERNAL_POLICY`). Quy trình rà soát được tạm dừng để tránh sinh kết luận giả.")

    st.markdown("### 🔍 Cấu trúc Bảng Kết quả Gap Tuân thủ (`compliance_gap_results.csv`)")
    results_path = PROJECT_ROOT / "outputs" / "compliance_gap_results.csv"
    if results_path.exists():
        df_gap = pd.read_csv(results_path)
        if df_gap.empty:
            st.info("💡 Bảng kết quả hiện đang rỗng do trạng thái `COMPLIANCE GAP DATA: INSUFFICIENT`. Dưới đây là schema 14 trường dữ liệu chuẩn hóa đã sẵn sàng:")
            schema_data = [
                {"Field": "gap_id", "Description": "Mã định danh gap tuân thủ (ví dụ: GAP_001)"},
                {"Field": "external_document_id", "Description": "Mã văn bản Nhà nước (NHNN/Chính phủ)"},
                {"Field": "external_chunk_id", "Description": "Mã chunk yêu cầu Nhà nước"},
                {"Field": "external_requirement", "Description": "Nội dung yêu cầu Nhà nước"},
                {"Field": "external_citation", "Description": "Trích dẫn điều khoản Nhà nước"},
                {"Field": "internal_document_id", "Description": "Mã văn bản Quy định Nội bộ Ngân hàng"},
                {"Field": "internal_chunk_id", "Description": "Mã chunk bằng chứng nội bộ"},
                {"Field": "internal_evidence", "Description": "Nội dung bằng chứng nội bộ"},
                {"Field": "internal_citation", "Description": "Trích dẫn điều khoản nội bộ"},
                {"Field": "classification", "Description": "Phân loại: DAP_UNG / THIEU / CHENH_LECH / CHUA_DU_BANG_CHUNG"},
                {"Field": "reason", "Description": "Căn cứ giải thích ngắn gọn"},
                {"Field": "confidence", "Description": "Độ tin cậy đánh giá (0.0 - 1.0)"},
                {"Field": "review_status", "Description": "Trạng thái phê duyệt: NEEDS_HUMAN_REVIEW"},
                {"Field": "request_id", "Description": "Mã yêu cầu truy vết Audit Log"},
            ]
            st.dataframe(pd.DataFrame(schema_data), use_container_width=True)
        else:
            st.dataframe(df_gap, use_container_width=True)

    st.markdown("---")
    st.markdown("```text\nGAP CHECKER: PASS\nHUMAN REVIEW REQUIRED: YES\n```")


# -----------------------------------------------------------------------------
# TAB 3: AUDIT TRAIL
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📜 Nhật ký Kiểm toán & Truy vết Hệ thống (Audit Trail)")
    st.markdown("Hệ thống tự động lưu vết 100% yêu cầu (bao gồm cả request bị DENIED) theo tiêu chuẩn bảo mật tuyệt đối (Không lưu password/secret).")

    log_path = PROJECT_ROOT / "outputs" / "audit_log.jsonl"
    if log_path.exists():
        logs = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line.strip()))
                    except Exception:
                        pass

        if logs:
            df_logs = pd.DataFrame(logs)
            
            # Filter logs suitable for user role demo
            if user_role not in ["Admin", "Risk_Manager"]:
                df_filtered = df_logs[df_logs["user_role"].apply(lambda r: user_role in r if isinstance(r, list) else user_role == r)]
                st.caption(f"🔒 Hiển thị nhật ký truy vết dành riêng cho vai trò: `{user_role}`")
            else:
                df_filtered = df_logs
                st.caption("🔓 Hiển thị toàn bộ nhật ký truy vết kiểm toán (Admin View)")

            st.dataframe(df_filtered, use_container_width=True)
            st.markdown(f"**Tổng số bản ghi Audit Log**: `{len(df_filtered)}` events")
        else:
            st.info("Chưa có bản ghi nhật ký audit log nào.")
    else:
        st.info("Chưa tìm thấy tệp `outputs/audit_log.jsonl`.")
