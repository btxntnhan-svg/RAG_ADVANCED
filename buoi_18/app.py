"""Streamlit Enterprise Application for Buoi 18: AI Compliance & Audit System (Agribank)."""

import json
from pathlib import Path
import sys
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(WORKSPACE_ROOT / "buoi_17"))

from scripts.audit_checklist_gen import AuditChecklistGenerator
from scripts.compliance_checker import ComplianceCheckerEngine

# Set Page Config
st.set_page_config(
    page_title="AI Compliance & Audit System — Agribank (Buổi 18)",
    page_icon="🏦",
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
        .badge-high { background-color: #dc3545; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
        .badge-medium { background-color: #ffc107; color: #111; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
        .badge-low { background-color: #28a745; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
        .card { background-color: #1e222a; padding: 20px; border-radius: 8px; border: 1px solid #2d3139; margin-bottom: 16px; }
        .evidence-box { background-color: #161920; padding: 12px; border-left: 4px solid #1f77b4; border-radius: 4px; font-size: 0.9em; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Training Recommendation Banner
st.warning("⚠️ **Demo sản phẩm AI Kiểm toán — Kết quả gợi ý cần kiểm toán viên xác minh trước khi ban hành.**")

# Sidebar Configuration
st.sidebar.title("🛡️ Cấu hình Quyền & Người dùng")
st.sidebar.markdown("---")

user_id_demo = st.sidebar.text_input("User ID Demo", value="USR_AUDITOR_01")
user_role = st.sidebar.selectbox(
    "User Role (Vai trò)",
    options=["Admin", "Risk Manager", "KiemToanVien", "Staff"],
    index=0,
)

st.sidebar.markdown("### 📊 Trạng thái Dữ liệu")
st.sidebar.success("🟢 24 Chunks Quy định Nội bộ Agribank")
st.sidebar.success("🟢 787 Chunks Văn bản Pháp luật Nhà nước")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Session / Clean Audit Log"):
    st.session_state.clear()
    st.sidebar.info("Đã làm mới Session State thành công!")

st.sidebar.caption("Hệ thống RAG AI Compliance & Audit — Buổi 18 (Agribank Enterprise)")

# Main Header
st.title("🏦 AI COMPLIANCE & AUDIT SYSTEM — AGRIBANK (BUỔI 18)")
st.markdown(f"**Người dùng**: `{user_id_demo}` | **Vai trò**: `<span class='badge-low'>{user_role}</span>`", unsafe_allow_html=True)
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
    st.subheader("🔍 UC3: AI Compliance Checker — Rà soát Mâu thuẫn & Chênh lệch Quy định")
    st.markdown("Hệ thống tự động so sánh chéo giữa Quy định Nội bộ Agribank và Văn bản Quy phạm Pháp luật Nhà nước để phát hiện xung đột hạn mức, quy trình và thẩm quyền.")

    col_dom, col_btn = st.columns([3, 1])
    with col_dom:
        domain_choice = st.selectbox(
            "Chọn Domain Nghiệp vụ cần Rà soát:",
            options=[
                "-- Quét Toàn bộ Các Domain --",
                "An toàn kho quỹ & Vận chuyển tiền",
                "CAR & Quản lý rủi ro",
                "Tín dụng & Thẩm quyền phê duyệt",
                "Ngoại tệ & Thanh toán Quốc tế",
                "Bảo mật CNTT & AI",
            ],
        )

    if st.button("🚀 Phát hiện Xung đột & Mâu thuẫn Tuân thủ"):
        with st.spinner("Đang truy xuất Evidence Package & Phân tích xung đột..."):
            checker = ComplianceCheckerEngine()

            test_pairs = [
                {
                    "domain": "An toàn kho quỹ & Vận chuyển tiền",
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
                    "domain": "Tín dụng & Thẩm quyền phê duyệt",
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
                        <h4>Mã Mâu thuẫn: <code>{item['conflict_id']}</code> | Domain: <b>{item['domain']}</b></h4>
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

                st.markdown("**🤖 Phân tích & Giải thích từ AI:**")
                st.info(item["description"])

                if st.button(f"✅ Phê duyệt / Đã xác minh (`{item['conflict_id']}`)", key=item["conflict_id"]):
                    item["review_status"] = "APPROVED_BY_AUDITOR"
                    st.success(f"Đã cập nhật trạng thái phê duyệt cho mã `{item['conflict_id']}` thành APPROVED_BY_AUDITOR!")

                st.markdown("---")

        # Download options
        df_conflicts = pd.DataFrame(results)
        csv_data = df_conflicts.to_csv(index=False, encoding="utf-8-sig")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "📥 Tải Kết quả CSV (`compliance_conflicts.csv`)",
                data=csv_data,
                file_name="compliance_conflicts.csv",
                mime="text/csv",
            )


# -----------------------------------------------------------------------------
# TAB 2: UC4 - AI AUDIT CHECKLIST GENERATOR
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("📋 UC4: AI Audit Checklist Generator — Tự động Sinh Danh mục Kiểm toán")
    st.markdown("Hệ thống phân tích các quy định nội bộ và Thông tư NHNN để tự động đóng gói danh mục câu hỏi kiểm tra, rủi ro tiềm ẩn và khuyến nghị hành động.")

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

    if st.button("⚡ Tạo bản nháp Checklist Kiểm toán"):
        with st.spinner("Đang truy xuất quy định & Tự động sinh danh mục Checklist..."):
            gen = AuditChecklistGenerator()
            items = gen.generate_checklist(domain=domain_chk, unit_scope=unit_chk, user_role=user_role)
            st.session_state["checklist_items"] = items

    if "checklist_items" in st.session_state and st.session_state["checklist_items"]:
        items = st.session_state["checklist_items"]
        st.markdown(f"### 📋 Danh mục Checklist Sinh ra: `{len(items)}` Mục Kiểm tra")

        df_items = pd.DataFrame(items)
        st.dataframe(df_items[["item_id", "domain", "unit_scope", "audit_question", "risk_level", "review_status"]], use_container_width=True)

        st.markdown("### 🔍 Chi tiết từng Mục Kiểm tra & Trích dẫn Văn bản Gốc")
        for it in items:
            sev_class = "badge-high" if it["risk_level"] == "HIGH" else "badge-medium"
            with st.expander(f"📌 [{it['item_id']}] {it['audit_question'][:80]}..."):
                st.markdown(f"**Câu hỏi Kiểm toán**: *\"{it['audit_question']}\"*")
                st.markdown(f"**Rủi ro Tiềm ẩn**: <span class='{sev_class}'>{it['risk_level']}</span> - {it['risk_description']}", unsafe_allow_html=True)
                st.markdown(f"**Trích dẫn Căn cứ (Citation)**: `{it['source_citation']}`")
                st.markdown(f"**Khuyến nghị Hành động**: {it['recommendation']}")

        # Download options
        csv_chk = df_items.to_csv(index=False, encoding="utf-8-sig")
        json_chk = df_items.to_json(orient="records", force_ascii=False, indent=2)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.download_button(
                "📥 Tải Checklist CSV (`audit_checklist_results.csv`)",
                data=csv_chk,
                file_name="audit_checklist_results.csv",
                mime="text/csv",
            )
        with col_c2:
            st.download_button(
                "📥 Tải Checklist JSON (`audit_checklist_results.json`)",
                data=json_chk,
                file_name="audit_checklist_results.json",
                mime="application/json",
            )


# -----------------------------------------------------------------------------
# TAB 3: AUDIT TRAIL & SYSTEM LOGS
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📜 Nhật ký Kiểm toán & Truy vết Hệ thống (System Audit Logs)")
    st.markdown("Ghi vết bất biến 100% thao tác tra cứu, quét xung đột tuân thủ và sinh checklist kiểm toán theo tiêu chuẩn bảo mật tuyệt đối.")

    log_file = PROJECT_ROOT / "outputs" / "audit_log.jsonl"
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

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                action_filter = st.selectbox(
                    "Lọc theo Hành động (Action):",
                    options=["-- Tất cả Hành động --"] + list(df_logs["action"].unique()),
                )
            with col_f2:
                status_filter = st.selectbox(
                    "Lọc theo Trạng thái (Status):",
                    options=["-- Tất cả Trạng thái --"] + list(df_logs["status"].unique()),
                )

            df_display = df_logs
            if action_filter != "-- Tất cả Hành động --":
                df_display = df_display[df_display["action"] == action_filter]
            if status_filter != "-- Tất cả Trạng thái --":
                df_display = df_display[df_display["status"] == status_filter]

            st.dataframe(df_display, use_container_width=True)
            st.caption(f"Hiển thị {len(df_display)} / {len(df_logs)} bản ghi nhật ký hệ thống.")
        else:
            st.info("Chưa có bản ghi nhật ký nào trong file audit log.")
    else:
        st.info("Chưa tìm thấy tệp `outputs/audit_log.jsonl`.")
