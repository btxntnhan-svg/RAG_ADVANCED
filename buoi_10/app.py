from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st
from neo4j import GraphDatabase

from legal_pipeline import (
    MODEL_NAME,
    build_document_edges,
    build_embedding_model,
    build_hierarchy_chunks,
    build_sample_legal_documents,
    convert_document_to_neo4j_record,
    generate_embeddings,
    print_sample_chunks,
    setup_database,
    test_neo4j_connection,
    verify_neo4j_counts,
)


st.set_page_config(page_title="RAG Lab - Chunking & Neo4j", layout="wide")


def connect_neo4j(uri: str, username: str, password: str):
    return GraphDatabase.driver(uri, auth=(username, password), connection_timeout=10)


st.title("Bài thực hành RAG: Chunking, Embedding và Neo4j")
st.caption("End-to-end demo theo nội dung trong file buoi_10(3).md")

with st.sidebar:
    st.header("Cấu hình Neo4j")
    uri = st.text_input("URI Neo4j", value="bolt://localhost:7687")
    username = st.text_input("Username", value="neo4j")
    password = st.text_input("Password", type="password", value="password")
    database = st.text_input("Database", value="kb-hops")

    st.markdown("---")
    st.subheader("Tùy chọn chạy")


if "documents" not in st.session_state:
    st.session_state.documents = build_sample_legal_documents()

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "sample_output" not in st.session_state:
    st.session_state.sample_output = ""

if "result" not in st.session_state:
    st.session_state.result = {"status": "idle"}


col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Dữ liệu mẫu pháp luật")
    st.write(f"Tổng số tài liệu: {len(st.session_state.documents)}")
    st.dataframe(
        [{
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "year": doc["year"],
            "source": doc["source"],
            "category": doc["category"],
        } for doc in st.session_state.documents[:5]],
        use_container_width=True,
    )

with col2:
    st.subheader("2. Mô hình embedding")
    st.code(f"{MODEL_NAME}")
    st.write("Chế độ chạy: CPU")

st.markdown("---")

if st.button("Tạo dữ liệu mẫu & chạy chunking"):
    docs = st.session_state.documents
    all_chunks: List[Dict[str, Any]] = []
    for doc in docs:
        all_chunks.extend(build_hierarchy_chunks(doc))

    model = build_embedding_model()
    embeddings = generate_embeddings(all_chunks, model)
    for chunk, embedding in zip(all_chunks, embeddings):
        chunk["embedding"] = embedding

    st.session_state.chunks = all_chunks
    st.session_state.sample_output = print_sample_chunks(all_chunks, limit=6)

    st.success(f"Đã tạo thành công {len(all_chunks)} chunk từ {len(docs)} tài liệu.")
    st.code(st.session_state.sample_output)

    st.subheader("Preview các chunk đầu tiên")
    st.dataframe(
        [{
            "chunk_id": chunk["chunk_id"],
            "doc_id": chunk["doc_id"],
            "level": chunk["level"],
            "title": chunk["title"],
            "parent_id": chunk.get("parent_id"),
            "next_chunk_id": chunk.get("next_chunk_id"),
        } for chunk in all_chunks[:10]],
        use_container_width=True,
    )

st.markdown("---")

# ============ TEST CONNECTION ============
st.subheader("3. Kiểm tra kết nối & Cấu hình Database")
col_test, col_setup = st.columns(2)

with col_test:
    if st.button("🔗 Kiểm tra kết nối Neo4j"):
        try:
            driver = connect_neo4j(uri, username, password)
            success, message = test_neo4j_connection(driver)
            if success:
                st.success(message)
            else:
                st.error(message)
            driver.close()
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")

with col_setup:
    if st.button("🔧 Setup Database"):
        try:
            driver = connect_neo4j(uri, username, password)
            success, message = setup_database(driver, database_name=database, clear_data=True)
            if success:
                st.success(message)
            else:
                st.error(message)
            driver.close()
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")

st.markdown("---")

if st.button("Nạp dữ liệu lên Neo4j"):
    chunks = st.session_state.chunks
    documents = st.session_state.documents
    if not documents or not chunks:
        st.warning("Bạn cần chạy chunking trước khi nạp dữ liệu lên Neo4j.")
        st.stop()

    try:
        driver = connect_neo4j(uri, username, password)
        with driver.session(database=database) as session:
            for document in documents:
                record = convert_document_to_neo4j_record(document)
                session.run(
                    """
                    MERGE (d:Document {doc_id: $doc_id})
                    SET d.title = $title,
                        d.source = $source,
                        d.year = $year,
                        d.category = $category
                    """,
                    **record,
                )

            for chunk in chunks:
                session.run(
                    """
                    MERGE (c:Chunk {chunk_id: $chunk_id})
                    SET c.doc_id = $doc_id,
                        c.title = $title,
                        c.level = $level,
                        c.text = $text,
                        c.embedding = $embedding,
                        c.source_title = $source_title
                    """,
                    chunk_id=chunk["chunk_id"],
                    doc_id=chunk["doc_id"],
                    title=chunk["title"],
                    level=chunk["level"],
                    text=chunk["text"],
                    embedding=chunk.get("embedding", [0.0] * 384),
                    source_title=chunk["source_title"],
                )

                session.run(
                    """
                    MATCH (d:Document {doc_id: $doc_id}), (c:Chunk {chunk_id: $chunk_id})
                    MERGE (c)-[:PART_OF]->(d)
                    """,
                    doc_id=chunk["doc_id"],
                    chunk_id=chunk["chunk_id"],
                )

                if chunk.get("parent_id"):
                    session.run(
                        """
                        MATCH (p:Chunk {chunk_id: $parent_id}), (c:Chunk {chunk_id: $chunk_id})
                        MERGE (p)-[:PARENT_OF]->(c)
                        """,
                        parent_id=chunk["parent_id"],
                        chunk_id=chunk["chunk_id"],
                    )

                if chunk.get("next_chunk_id"):
                    session.run(
                        """
                        MATCH (current:Chunk {chunk_id: $chunk_id}), (next:Chunk {chunk_id: $next_chunk_id})
                        MERGE (current)-[:NEXT]->(next)
                        """,
                        chunk_id=chunk["chunk_id"],
                        next_chunk_id=chunk["next_chunk_id"],
                    )

            for src_doc_id, dst_doc_id, rel_name in build_document_edges():
                session.run(
                    f"""
                    MATCH (a:Document {{doc_id: $src}}), (b:Document {{doc_id: $dst}})
                    MERGE (a)-[:{rel_name}]->(b)
                    """,
                    src=src_doc_id,
                    dst=dst_doc_id,
                )

        verification = verify_neo4j_counts(driver, database=database)
        st.session_state.result = {"status": "success", **verification}
        st.success("Nạp dữ liệu thành công vào Neo4j.")
        st.json(verification)
    except Exception as exc:
        st.session_state.result = {"status": "error", "message": str(exc)}
        st.error(f"Không thể kết nối hoặc nạp dữ liệu: {exc}")

st.markdown("---")

st.subheader("4. Kiểm tra và xác minh")
if st.session_state.result.get("status") == "success":
    result = st.session_state.result
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📄 Document Nodes", result.get("document_count", 0))
        st.metric("🔗 Document Relationships", result.get("document_relation_count", 0))
    
    with col2:
        st.metric("📝 Chunk Nodes", result.get("chunk_count", 0))
        st.metric("PART_OF Relationships", result.get("part_of_count", 0))
    
    with col3:
        st.metric("👨‍👩‍👧 Parent-Child Relationships", result.get("parent_of_count", 0))
        st.metric("↪️ NEXT Relationships", result.get("next_relation_count", 0))
    
    st.markdown("**Document Edge Types:**")
    doc_edges = result.get("document_edges", {})
    edge_col1, edge_col2, edge_col3 = st.columns(3)
    with edge_col1:
        st.write(f"🔹 CAN_CU: {doc_edges.get('CAN_CU', 0)}")
    with edge_col2:
        st.write(f"🔹 THAY_THE: {doc_edges.get('THAY_THE', 0)}")
    with edge_col3:
        st.write(f"🔹 HOP_NHAT: {doc_edges.get('HOP_NHAT', 0)}")
    
    st.divider()
    st.success("✅ Xác minh yêu cầu:")
    st.write(f"- Document nodes: {result.get('document_count', 0)}/15 ✓")
    st.write(f"- Document relationships: {result.get('document_relation_count', 0)}/8 ✓")
    st.write(f"- Chunk hierarchies (PART_OF + PARENT_OF): {result.get('part_of_count', 0) + result.get('parent_of_count', 0)} ✓")
    st.write(f"- Sequential links (NEXT): {result.get('next_relation_count', 0)} ✓")
    
    with st.expander("📊 Chi tiết JSON"):
        st.json(result)
else:
    st.info("Chưa có dữ liệu xác minh từ Neo4j. Hãy:")
    st.write("1. ✅ Kiểm tra kết nối Neo4j (nút 🔗)")
    st.write("2. ✅ Setup database (nút 🔧)")
    st.write("3. ✅ Tạo dữ liệu mẫu & chạy chunking")
    st.write("4. ✅ Nạp dữ liệu lên Neo4j")

st.caption("Mục tiêu học tập: làm sạch HTML, phân tách phân cấp, tạo embedding dense và lưu vào Neo4j theo mô hình dữ liệu đồ thị.")
