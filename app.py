"""Streamlit Enterprise Application for Buoi 19: Local AI Compliance & Audit System (Agribank)."""

import json
import os
from pathlib import Path
import sys
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from scripts.audit_checklist_gen import AuditChecklistGenerator
from scripts.compliance_checker import ComplianceCheckerEngine
from scripts.ollama_adapter import OllamaClient

# Set Page Config
st.set_page_config(
    page_title="AI Compliance & Audit System — Agribank",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Custom Clean White & Agribank Red Theme CSS
st.markdown(
    """
    <meta name="google" content="notranslate">
    <style>
        /* Main background & Typography */
        .stApp, .main { 
            background-color: #FFFFFF !important; 
            color: #0F172A !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #C8102E !important;
            font-weight: 700 !important;
        }
        h4, h5, h6 {
            color: #1E293B !important;
            font-weight: 600 !important;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #F8FAFC !important;
            border-right: 1px solid #E2E8F0 !important;
        }
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {
            color: #C8102E !important;
        }
        
        /* Primary Buttons */
        .stButton>button {
            width: 100%;
            background-color: #C8102E !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            border-radius: 6px !important;
            border: 1px solid #A71D2A !important;
            padding: 10px 16px !important;
            box-shadow: 0 2px 4px rgba(200, 16, 46, 0.15) !important;
            transition: all 0.2s ease-in-out !important;
        }
        .stButton>button:hover { 
            background-color: #A71D2A !important; 
            color: #FFFFFF !important;
            box-shadow: 0 4px 8px rgba(200, 16, 46, 0.25) !important;
        }
        
        /* Badges */
        .badge-high { 
            background-color: #DC2626; 
            color: #FFFFFF; 
            padding: 4px 10px; 
            border-radius: 4px; 
            font-weight: bold; 
            font-size: 0.85em;
        }
        .badge-medium { 
            background-color: #D97706; 
            color: #FFFFFF; 
            padding: 4px 10px; 
            border-radius: 4px; 
            font-weight: bold; 
            font-size: 0.85em;
        }
        .badge-low { 
            background-color: #059669; 
            color: #FFFFFF; 
            padding: 4px 10px; 
            border-radius: 4px; 
            font-weight: bold; 
            font-size: 0.85em;
        }
        .badge-provider {
            background-color: #C8102E; 
            color: #FFFFFF; 
            padding: 4px 10px; 
            border-radius: 4px; 
            font-weight: bold; 
            font-size: 0.85em;
        }
        
        /* Card Containers */
        .card { 
            background-color: #F8FAFC !important; 
            padding: 20px !important; 
            border-radius: 8px !important; 
            border: 1px solid #E2E8F0 !important; 
            border-left: 5px solid #C8102E !important;
            margin-bottom: 16px !important; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        }
        .card h4 {
            color: #C8102E !important;
            margin-top: 0 !important;
        }
        
        /* Evidence Text Boxes */
        .evidence-box { 
            background-color: #FFF5F5 !important; 
            color: #0F172A !important;
            padding: 14px !important; 
            border-left: 4px solid #C8102E !important; 
            border-radius: 4px !important; 
            font-size: 0.92em !important; 
            line-height: 1.5 !important;
            border-top: 1px solid #FFE4E6 !important;
            border-right: 1px solid #FFE4E6 !important;
            border-bottom: 1px solid #FFE4E6 !important;
        }
        
        /* Tabs Header */
        .stTabs [data-baseweb="tab-list"] {
            border-bottom: 2px solid #E2E8F0 !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-weight: bold !important;
            color: #475569 !important;
        }
        .stTabs [aria-selected="true"] {
            color: #C8102E !important;
            border-bottom-color: #C8102E !important;
        }

        /* Inputs & Selectboxes text readability */
        div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border-color: #CBD5E1 !important;
        }
        input {
            color: #0F172A !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Active Provider Detection
llm_provider = os.getenv("LLM_PROVIDER", "ollama").upper()

# Banner
st.warning("⚠️ **HỆ THỐNG AI KIỂM TOÁN NỘI BỘ AGRIBANK — RÀ SOÁT TUÂN THỦ TỰ ĐỘNG**")

# Sidebar Configuration
st.sidebar.title("🛡️ Quản trị & Môi trường AI")
st.sidebar.markdown("---")

user_id_demo = st.sidebar.text_input("Cán bộ Kiểm toán (User ID)", value="USR_AUDITOR_01")
user_role = st.sidebar.selectbox(
    "Vai trò (User Role)",
    options=["Admin", "Risk_Manager", "Compliance", "Auditor", "Staff"],
    index=0,
)

st.sidebar.markdown("### 🔌 Hạ tầng Model Engine")
st.sidebar.info(f"Mô hình tích hợp: **{llm_provider}** (Qwen3:0.6b Local)")
st.sidebar.success("🟢 24 Chunks Quy định Nội bộ Agribank")
st.sidebar.success("🟢 787 Chunks Văn bản Pháp luật NHNN")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Làm mới Session / Audit Log"):
    st.session_state.clear()
    st.sidebar.info("Đã làm mới Session State!")

st.sidebar.caption("Hệ thống RAG Local AI Compliance & Audit — Buổi 19 Containerized")

# Main Header
st.title("🏦 AGRIBANK AI COMPLIANCE & AUDIT SYSTEM")
st.markdown(
    f"**Cán bộ**: `{user_id_demo}` | **Vai trò**: <span class='badge-low'>{user_role}</span> | "
    f"**LLM Provider**: <span class='badge-provider'>{llm_provider} (Local Model Qwen3:0.6b)</span>",
    unsafe_allow_html=True
)
st.markdown("---")

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs([
    "🔍 TAB 1: UC3 - AI COMPLIANCE CHECKER",
    "📋 TAB 2: UC4 - AI AUDIT CHECKLIST GENERATOR",
    "📜 TAB 3: AUDIT TRAIL & SYSTEM LOGS",
])


# -----------------------------------------------------------------------------
# TAB 1: UC3 - AI COMPLIANCE CHECKER
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("🔍 UC3: Rà soát Mâu thuẫn & Chênh lệch Quy định Tuân thủ")
    st.markdown("Hệ thống đối soát tự động giữa Quy định Nội bộ Agribank và Văn bản Pháp luật Nhà nước để phát hiện xung đột hạn mức, quy trình và thẩm quyền.")

    col_dom, col_btn = st.columns([3, 1])
    with col_dom:
        domain_choice = st.selectbox(
            "Chọn Domain Nghiệp vụ cần Rà soát:",
            options=[
                "-- Quét Toàn bộ Các Domain --",
                "An toàn kho quỹ & Vận chuyển tiền mặt",
                "CAR & Quản lý rủi ro",
                "Tín dụng & Phân cấp phê duyệt",
            ],
        )

    if st.button("🚀 Thực hiện Rà soát Mâu thuẫn Tuân thủ"):
        with st.spinner("Đang truy xuất văn bản & Phân tích xung đột bằng Local Model Qwen3:0.6b..."):
            checker = ComplianceCheckerEngine()

            test_pairs = [
                {
                    "domain": "An toàn kho quỹ & Vận chuyển tiền mặt",
                    "doc_a_id": "agr_at01",
                    "doc_b_id": "44209",
                    "query": "Quy trình giao nhận kiểm đếm và niêm phong kho tiền",
                },
                {
                    "domain": "CAR & Quản lý rủi ro",
                    "doc_a_id": "agr_car02",
                    "doc_b_id": "117310",
                    "query": "Tỷ lệ an toàn vốn tối thiểu CAR và định mức rủi ro",
                },
                {
                    "domain": "Tín dụng & Phân cấp phê duyệt",
                    "doc_a_id": "agr_td03",
                    "doc_b_id": "168220",
                    "query": "Hạn mức phán quyết ủy quyền cho vay tín dụng",
                },
            ]

            if domain_choice != "-- Quét Toàn bộ Các Domain --":
                test_pairs = [p for p in test_pairs if p["domain"].lower() == domain_choice.lower()]

            results = []
            for tp in test_pairs:
                res = checker.analyze_conflict_pair(
                    domain=tp["domain"],
                    doc_a_id=tp["doc_a_id"],
                    doc_b_id=tp["doc_b_id"],
                    topic_query=tp["query"],
                    user_role=user_role,
                )
                results.append(res)

            st.session_state["conflicts_results"] = results

    if "conflicts_results" in st.session_state and st.session_state["conflicts_results"]:
        results = st.session_state["conflicts_results"]
        st.markdown(f"### 📊 Kết quả Phát hiện: `{len(results)}` Xung đột / Chênh lệch Tuân thủ")

        for item in results:
            severity_class = "badge-high" if item["severity"] == "HIGH" else ("badge-medium" if item["severity"] == "MEDIUM" else "badge-low")
            
            with st.container():
                st.markdown(
                    f"""
                    <div class="card">
                        <h4>📌 Mã Mâu thuẫn: <code>{item['conflict_id']}</code> | Domain: <b>{item['domain']}</b></h4>
                        <p>
                            <span class="{severity_class}">Mức độ: {item['severity']}</span> &nbsp;
                            <span class="badge-medium">Loại: {item['conflict_type']}</span> &nbsp;
                            <span class="badge-low">Trạng thái: {item['review_status']}</span>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("##### 📄 Văn bản A (Quy định Nội bộ Agribank)")
                    st.caption(f"Trích dẫn: `{item['doc_a_citation']}`")
                    st.markdown(f"<div class='evidence-box'>{item['doc_a_text']}</div>", unsafe_allow_html=True)

                with col_b:
                    st.markdown("##### 🏛️ Văn bản B (Pháp luật Nhà nước / Tham chiếu)")
                    st.caption(f"Trích dẫn: `{item['doc_b_citation']}`")
                    st.markdown(f"<div class='evidence-box'>{item['doc_b_text']}</div>", unsafe_allow_html=True)

                st.markdown("**🤖 Phân tích & Mô tả Mâu thuẫn từ AI:**")
                st.info(item["description"])

                if st.button(f"✅ Xác minh Phê duyệt (`{item['conflict_id']}`)", key=item["conflict_id"]):
                    item["review_status"] = "APPROVED_BY_AUDITOR"
                    st.success(f"Đã xác minh và ghi nhận phê duyệt cho mã `{item['conflict_id']}`!")

                st.markdown("---")

        # Download options
        df_conflicts = pd.DataFrame(results)
        csv_data = df_conflicts.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 Tải Bảng Mâu thuẫn Tuân thủ CSV (`compliance_conflicts.csv`)",
            data=csv_data,
            file_name="compliance_conflicts.csv",
            mime="text/csv",
        )


# -----------------------------------------------------------------------------
# TAB 2: UC4 - AI AUDIT CHECKLIST GENERATOR
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("📋 UC4: Tự động Sinh Danh mục Kiểm tra Kiểm toán (Audit Checklist)")
    st.markdown("Hệ thống tự động phân tích quy định và sinh câu hỏi kiểm tra, mô tả rủi ro tiềm ẩn và khuyến nghị hành động kiểm toán.")

    col_d, col_u = st.columns(2)
    with col_d:
        domain_chk = st.selectbox(
            "Miền Kiểm toán (Domain Scope):",
            options=["An toàn kho quỹ & Vận chuyển tiền", "Bảo mật CNTT & AI"],
        )
    with col_u:
        unit_chk = st.selectbox(
            "Đơn vị Được Kiểm toán (Unit Scope):",
            options=["Chi nhánh loại 1", "Phòng Giao dịch", "Khối CNTT & Vận hành AI", "Phòng Kế toán"],
        )

    if st.button("⚡ Sinh Danh mục Checklist Kiểm toán"):
        with st.spinner("Đang tổng hợp dữ liệu & Sinh checklist kiểm toán bằng Local AI..."):
            gen = AuditChecklistGenerator()
            items = gen.generate_checklist(domain=domain_chk, unit_scope=unit_chk, user_role=user_role)
            st.session_state["checklist_items"] = items

    if "checklist_items" in st.session_state and st.session_state["checklist_items"]:
        items = st.session_state["checklist_items"]
        st.markdown(f"### 📋 Danh mục Checklist Sinh ra: `{len(items)}` Mục Kiểm tra")

        df_items = pd.DataFrame(items)
        st.dataframe(df_items[["item_id", "domain", "unit_scope", "audit_question", "risk_level", "review_status"]], use_container_width=True)

        st.markdown("### 🔍 Chi tiết từng Mục Kiểm tra & Trích dẫn Căn cứ")
        for it in items:
            sev_class = "badge-high" if it["risk_level"] == "HIGH" else "badge-medium"
            with st.expander(f"📌 [{it['item_id']}] {it['audit_question'][:80]}..."):
                st.markdown(f"**Câu hỏi Kiểm toán**: *\"{it['audit_question']}\"*")
                st.markdown(f"**Rủi ro Tiềm ẩn**: <span class='{sev_class}'>{it['risk_level']}</span> - {it['risk_description']}", unsafe_allow_html=True)
                st.markdown(f"**Trích dẫn Căn cứ (Source Citation)**: `{it['source_citation']}`")
                st.markdown(f"**Khuyến nghị Hành động**: {it['recommendation']}")

        # Download options
        csv_chk = df_items.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 Tải Checklist Kiểm toán CSV (`audit_checklist_results.csv`)",
            data=csv_chk,
            file_name="audit_checklist_results.csv",
            mime="text/csv",
        )


# -----------------------------------------------------------------------------
# TAB 3: AUDIT TRAIL & SYSTEM LOGS
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📜 Nhật ký Truy vết & Kiểm toán Hệ thống (System Audit Logs)")
    st.markdown("Ghi vết bất biến 100% các thao tác tra cứu, rà soát mâu thuẫn và sinh checklist của người dùng theo tiêu chuẩn bảo mật tuyệt đối.")

    log_file = PROJECT_ROOT / "outputs" / "audit_log.jsonl"
    if not log_file.exists():
        log_file = PROJECT_ROOT / "outputs" / "audit_trail.jsonl"

    if log_file.exists():
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line.strip()))
                    except Exception:
                        pass

        if logs:
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs, use_container_width=True)
            st.caption(f"Hiển thị {len(df_logs)} bản ghi nhật ký hệ thống.")
        else:
            st.info("Chưa có bản ghi nhật ký nào trong file audit log.")
    else:
        st.info("Chưa tìm thấy tệp `outputs/audit_log.jsonl`.")
