import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import subprocess
from datetime import datetime

# ============================================================================
# Config
# ============================================================================
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# ============================================================================
# Page Config
# ============================================================================
st.set_page_config(
    page_title="Legal KB Graph",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# Helper Functions
# ============================================================================


@st.cache_resource
def get_neo4j_driver():
    """Kết nối Neo4j driver."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session(database=NEO4J_DATABASE) as session:
            session.run("RETURN 1 AS ok")
        return driver
    except Exception as e:
        st.error(f"Neo4j connection failed: {e}")
        return None


def load_csv(filename):
    """Tải file CSV từ folder."""
    path = ROOT / filename
    if path.exists():
        return pd.read_csv(path, keep_default_na=False)
    return None


def query_neo4j(query, params=None):
    """Chạy query Neo4j."""
    driver = get_neo4j_driver()
    if not driver:
        return []
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]
    except Exception as e:
        st.error(f"Query error: {e}")
        return []


# ============================================================================
# Main Sections
# ============================================================================


def page_dashboard():
    """Trang Dashboard."""
    st.title("⚖️ Legal KB Dashboard")

    # Kết nối check
    driver = get_neo4j_driver()
    if not driver:
        st.error("❌ Neo4j not connected")
        return

    # Lấy thống kê
    col1, col2, col3, col4, col5 = st.columns(5)

    # Node count
    with col1:
        nodes_result = query_neo4j("MATCH (n) RETURN count(n) AS total")
        total_nodes = nodes_result[0]["total"] if nodes_result else 0
        st.metric("Total Nodes", f"{total_nodes:,}")

    # Relationship count
    with col2:
        rels_result = query_neo4j("MATCH ()-[r]->() RETURN count(r) AS total")
        total_rels = rels_result[0]["total"] if rels_result else 0
        st.metric("Total Relationships", f"{total_rels:,}")

    # Documents
    with col3:
        doc_result = query_neo4j("MATCH (d:Document) RETURN count(d) AS total")
        total_docs = doc_result[0]["total"] if doc_result else 0
        st.metric("Documents", f"{total_docs:,}")

    # Entities
    with col4:
        entity_result = query_neo4j(
            "MATCH (n:CoQuan|NguoiKy|DoiTuongApDung|LinhVuc) RETURN count(n) AS total"
        )
        total_entities = entity_result[0]["total"] if entity_result else 0
        st.metric("Entities", f"{total_entities:,}")

    # Relationship Types
    with col5:
        rel_type_result = query_neo4j(
            "MATCH ()-[r]->() RETURN type(r) AS rel_type, count(*) AS cnt"
        )
        total_rel_types = len(rel_type_result)
        st.metric("Rel. Types", f"{total_rel_types}")

    st.divider()

    # Node distribution by label
    st.subheader("📊 Node Distribution")
    node_dist = query_neo4j("MATCH (n) RETURN labels(n) AS labels, count(*) AS cnt ORDER BY cnt DESC")
    if node_dist:
        node_labels = []
        node_counts = []
        for row in node_dist:
            label = row["labels"][0] if row["labels"] else "Unknown"
            node_labels.append(label)
            node_counts.append(row["cnt"])

        fig = px.pie(values=node_counts, names=node_labels, title="Nodes by Label")
        st.plotly_chart(fig, use_container_width=True)

    # Relationship distribution
    st.subheader("🔗 Relationship Distribution")
    rel_dist = query_neo4j("MATCH ()-[r]->() RETURN type(r) AS rel_type, count(*) AS cnt ORDER BY cnt DESC")
    if rel_dist:
        rel_types = [row["rel_type"] for row in rel_dist]
        rel_counts = [row["cnt"] for row in rel_dist]

        fig = px.bar(
            x=rel_types,
            y=rel_counts,
            title="Relationships by Type",
            labels={"x": "Relationship Type", "y": "Count"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # Co-agencies (cơ quan ban hành)
    st.subheader("🏛️ Documents by Agency")
    agency_result = query_neo4j(
        """
        MATCH (d:Document)-[:BAN_HANH_BOI]->(c:CoQuan)
        RETURN c.name AS agency, count(d) AS num_docs
        ORDER BY num_docs DESC
        """
    )
    if agency_result:
        agencies = [row["agency"] for row in agency_result]
        doc_counts = [row["num_docs"] for row in agency_result]
        fig = px.bar(x=agencies, y=doc_counts, title="Documents by Issuing Agency")
        st.plotly_chart(fig, use_container_width=True)


def page_documents():
    """Trang Browse Documents."""
    st.title("📄 Document Browser")

    cleaned = load_csv("cleaned_documents.csv")
    if cleaned is None:
        st.warning("cleaned_documents.csv not found")
        return

    # Search
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search_id = st.text_input("Search by ID", placeholder="e.g., 112025")
    with col2:
        search_title = st.text_input("Search by Title", placeholder="e.g., Nghị định")
    with col3:
        st.write("")

    # Filter
    if search_id:
        cleaned = cleaned[cleaned["id"].astype(str).str.contains(search_id, na=False)]
    if search_title:
        cleaned = cleaned[cleaned["title"].astype(str).str.contains(search_title, case=False, na=False)]

    # Display
    st.subheader(f"Found {len(cleaned)} documents")
    
    if len(cleaned) > 0:
        # Table view
        display_cols = ["id", "so_ky_hieu", "title", "ngay_ban_hanh", "co_quan_ban_hanh", "nguoi_ky"]
        st.dataframe(cleaned[display_cols], use_container_width=True, height=400)

        # Detail view
        st.subheader("📋 Document Details")
        selected_idx = st.selectbox(
            "Select document to view:",
            range(len(cleaned)),
            format_func=lambda i: f"{cleaned.iloc[i]['so_ky_hieu']} - {cleaned.iloc[i]['title'][:50]}",
        )

        doc = cleaned.iloc[selected_idx]
        col1, col2 = st.columns(2)

        with col1:
            st.write("**ID:**", doc["id"])
            st.write("**So ky hieu:**", doc["so_ky_hieu"])
            st.write("**Loai van ban:**", doc["loai_van_ban"])
            st.write("**Ngay ban hanh:**", doc["ngay_ban_hanh"])
            st.write("**Co quan ban hanh:**", doc["co_quan_ban_hanh"])

        with col2:
            st.write("**Nguoi ky:**", doc["nguoi_ky"])
            st.write("**Pham vi ap dung:**", doc["pham_vi"])
            st.write("**Linh vuc:**", doc["linh_vuc"])
            st.write("**Nganh:**", doc["nganh"])
            st.write("**Tinh trang hieu luc:**", doc["tinh_trang_hieu_luc"])

        # Content preview
        with st.expander("📖 Content Preview"):
            content_text = doc.get("content_clean", "")[:1000]
            st.text_area("Content (first 1000 chars):", content_text, height=200, disabled=True)

        # Neo4j info
        st.subheader("🔗 Graph Relations")
        doc_id = doc["id"]
        driver = get_neo4j_driver()
        if driver:
            rels_result = query_neo4j(
                """
                MATCH (d:Document {id: $id})-[r]->(n)
                RETURN type(r) AS rel_type, labels(n) AS labels, n.name AS name
                """,
                {"id": str(doc_id)},
            )
            if rels_result:
                for rel in rels_result:
                    label = rel["labels"][0] if rel["labels"] else "Entity"
                    st.write(f"- **{rel['rel_type']}** → {label}: `{rel['name']}`")
            else:
                st.info("No relations found for this document in graph.")


def page_entities():
    """Trang Browse Entities."""
    st.title("🏢 Entity Browser")

    entities_csv = load_csv("entities.csv")
    if entities_csv is None:
        st.warning("entities.csv not found")
        return

    # Entity type filter
    entity_type = st.selectbox(
        "Filter by Entity Type",
        ["All"] + sorted(entities_csv["entity_type"].unique().tolist()),
    )

    if entity_type != "All":
        filtered = entities_csv[entities_csv["entity_type"] == entity_type]
    else:
        filtered = entities_csv

    st.subheader(f"Found {len(filtered)} entities")

    # Display
    display_cols = ["entity_id", "entity_type", "canonical_name", "original_name", "confidence"]
    st.dataframe(filtered[display_cols], use_container_width=True, height=400)

    # Statistics
    st.subheader("📊 Entity Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Entities", len(entities_csv))

    with col2:
        unique_types = entities_csv["entity_type"].nunique()
        st.metric("Entity Types", unique_types)

    with col3:
        avg_conf = entities_csv["confidence"].mean()
        st.metric("Avg Confidence", f"{avg_conf:.2f}")

    # Distribution
    entity_dist = entities_csv["entity_type"].value_counts()
    fig = px.pie(values=entity_dist.values, names=entity_dist.index, title="Entities by Type")
    st.plotly_chart(fig, use_container_width=True)


def page_relationships():
    """Trang Browse Relationships."""
    st.title("🔗 Relationship Browser")

    rels_csv = load_csv("relationships.csv")
    if rels_csv is None:
        st.warning("relationships.csv not found")
        return

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        rel_type_filter = st.selectbox(
            "Filter by Relationship Type",
            ["All"] + sorted(rels_csv["relationship_type"].unique().tolist()),
        )
    with col2:
        method_filter = st.selectbox(
            "Filter by Method",
            ["All"] + sorted(rels_csv["method"].unique().tolist()),
        )

    # Apply filters
    filtered = rels_csv
    if rel_type_filter != "All":
        filtered = filtered[filtered["relationship_type"] == rel_type_filter]
    if method_filter != "All":
        filtered = filtered[filtered["method"] == method_filter]

    st.subheader(f"Found {len(filtered)} relationships")

    # Display
    display_cols = ["source", "target", "relationship_type", "method", "confidence"]
    st.dataframe(filtered[display_cols], use_container_width=True, height=400)

    # Statistics
    st.subheader("📊 Relationship Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Relationships", len(rels_csv))

    with col2:
        rel_types = rels_csv["relationship_type"].nunique()
        st.metric("Relationship Types", rel_types)

    with col3:
        avg_conf = rels_csv["confidence"].mean()
        st.metric("Avg Confidence", f"{avg_conf:.2f}")

    # Type distribution
    rel_type_dist = rels_csv["relationship_type"].value_counts()
    fig = px.bar(
        x=rel_type_dist.index,
        y=rel_type_dist.values,
        title="Relationships by Type",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Validation report
    st.subheader("⚠️ Validation Report")
    val_csv = load_csv("validation_report.csv")
    if val_csv is not None:
        st.metric("Invalid Relationships", len(val_csv))
        if len(val_csv) > 0:
            val_type_dist = val_csv["rejection_reason"].value_counts()
            fig = px.pie(
                values=val_type_dist.values,
                names=val_type_dist.index,
                title="Invalid Relationships by Reason",
            )
            st.plotly_chart(fig, use_container_width=True)


def page_graph_explorer():
    """Trang Graph Explorer."""
    st.title("🕸️ Graph Explorer")

    driver = get_neo4j_driver()
    if not driver:
        st.error("Neo4j connection failed")
        return

    # Query builder
    st.subheader("Query Samples")

    sample_queries = {
        "All Documents": "MATCH (d:Document) RETURN d.id AS id, d.so_ky_hieu AS ky_hieu LIMIT 20",
        "Document → NguoiKy": "MATCH (d:Document)-[:KY_BOI]->(p:NguoiKy) RETURN d.id, d.so_ky_hieu, p.name LIMIT 10",
        "Document → CoQuan": "MATCH (d:Document)-[:BAN_HANH_BOI]->(c:CoQuan) RETURN d.id, d.so_ky_hieu, c.name LIMIT 10",
        "Document → DoiTuongApDung": "MATCH (d:Document)-[:AP_DUNG_CHO]->(o:DoiTuongApDung) RETURN d.id, d.so_ky_hieu, o.name LIMIT 10",
        "Document → LinhVuc": "MATCH (d:Document)-[:THUOC_LINH_VUC]->(l:LinhVuc) RETURN d.id, d.so_ky_hieu, l.name LIMIT 10",
        "Node Count by Label": "MATCH (n) RETURN labels(n) AS labels, count(*) AS cnt ORDER BY cnt DESC",
        "Relationship Count by Type": "MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS cnt ORDER BY cnt DESC",
    }

    query_choice = st.selectbox("Select query:", list(sample_queries.keys()))
    query = sample_queries[query_choice]

    # Custom query option
    if st.checkbox("Use custom Cypher query"):
        query = st.text_area("Enter Cypher query:", query, height=150)

    if st.button("🔍 Run Query"):
        results = query_neo4j(query)
        if results:
            st.subheader("Results")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True, height=400)

            # CSV download
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
        else:
            st.info("No results found")


def page_pipeline():
    """Trang Run Pipeline."""
    st.title("🔄 Pipeline Management")

    st.info(
        """
        Run the full knowledge graph pipeline.
        This will:
        1. Clean documents
        2. Extract candidate relations
        3. Extract entities
        4. Normalize entities
        5. Extract relationships
        6. Validate relationships
        7. Check Neo4j connectivity
        8. Import graph
        """
    )

    if st.button("▶️ Run Full Pipeline", type="primary", use_container_width=True):
        st.write("Running pipeline...")
        progress_bar = st.progress(0)

        try:
            # Run pipeline
            result = subprocess.run(
                [
                    str(ROOT / ".venv" / "Scripts" / "python.exe"),
                    str(ROOT / "ner_kb_pipeline.py"),
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=600,
            )

            # Show output
            st.subheader("Pipeline Output")
            if result.stdout:
                st.text(result.stdout)

            if result.stderr:
                st.warning("Stderr:")
                st.text(result.stderr)

            progress_bar.progress(100)

            if result.returncode == 0:
                st.success("✅ Pipeline completed successfully!")
            else:
                st.error(f"❌ Pipeline failed with code {result.returncode}")

        except subprocess.TimeoutExpired:
            st.error("❌ Pipeline timeout (10 minutes)")
        except Exception as e:
            st.error(f"❌ Error: {e}")


def page_stats():
    """Trang Statistics."""
    st.title("📈 Project Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Data Files")
        files_info = [
            ("cleaned_documents.csv", "Cleaned documents"),
            ("relation_candidates.csv", "Relation candidates"),
            ("extracted_entities_raw.csv", "Extracted entities"),
            ("enriched_metadata.csv", "Enriched metadata"),
            ("entities.csv", "Canonicalized entities"),
            ("relationships_raw.csv", "Raw relationships"),
            ("relationships.csv", "Validated relationships"),
            ("validation_report.csv", "Validation report"),
        ]

        for filename, desc in files_info:
            path = ROOT / filename
            if path.exists():
                size_mb = path.stat().st_size / (1024 * 1024)
                st.write(f"✅ {filename} ({size_mb:.2f} MB) - {desc}")
            else:
                st.write(f"❌ {filename} - {desc}")

    with col2:
        st.subheader("CSV Row Counts")
        for filename, _ in files_info:
            df = load_csv(filename)
            if df is not None:
                st.write(f"**{filename}:** {len(df)} rows")

    st.divider()

    # Detailed stats
    st.subheader("Detailed Statistics")

    cols_data = []

    cleaned = load_csv("cleaned_documents.csv")
    if cleaned is not None:
        cols_data.append(("cleaned_documents.csv", {
            "Total rows": len(cleaned),
            "Columns": len(cleaned.columns),
            "Missing values": cleaned.isna().sum().sum(),
        }))

    entities = load_csv("entities.csv")
    if entities is not None:
        cols_data.append(("entities.csv", {
            "Total rows": len(entities),
            "Unique types": entities["entity_type"].nunique(),
            "Avg confidence": f"{entities['confidence'].mean():.3f}",
        }))

    rels = load_csv("relationships.csv")
    if rels is not None:
        cols_data.append(("relationships.csv", {
            "Total rows": len(rels),
            "Relationship types": rels["relationship_type"].nunique(),
            "Avg confidence": f"{rels['confidence'].mean():.3f}",
        }))

    val = load_csv("validation_report.csv")
    if val is not None:
        cols_data.append(("validation_report.csv", {
            "Invalid rows": len(val),
            "Rejection reasons": val["rejection_reason"].nunique(),
        }))

    for filename, stats in cols_data:
        with st.expander(f"📊 {filename}"):
            for key, value in stats.items():
                st.write(f"- **{key}:** {value}")


# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.title("⚖️ Legal KB Graph")
    st.write("Knowledge Graph Browser & Manager")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Documents",
            "Entities",
            "Relationships",
            "Graph Explorer",
            "Pipeline",
            "Statistics",
        ],
    )

    st.divider()

    # Neo4j connection status
    st.subheader("Neo4j Status")
    driver = get_neo4j_driver()
    if driver:
        st.success("✅ Connected")
        try:
            with driver.session(database=NEO4J_DATABASE) as session:
                result = session.run("RETURN 1 AS ok")
                st.write(f"Database: **{NEO4J_DATABASE}**")
        except:
            st.error("❌ Query failed")
    else:
        st.error("❌ Not connected")

    st.info(f"URI: `{NEO4J_URI}`")

    st.divider()

    # About
    st.subheader("About")
    st.write(
        """
        This is a Knowledge Graph browser for Vietnamese legal documents.
        
        **Stack:**
        - Python, Pandas
        - Neo4j
        - Streamlit
        
        **Data:**
        - 30 legal documents
        - 70 nodes
        - 108 relationships
        """
    )


# ============================================================================
# Main Content
# ============================================================================

if page == "Dashboard":
    page_dashboard()
elif page == "Documents":
    page_documents()
elif page == "Entities":
    page_entities()
elif page == "Relationships":
    page_relationships()
elif page == "Graph Explorer":
    page_graph_explorer()
elif page == "Pipeline":
    page_pipeline()
elif page == "Statistics":
    page_stats()
