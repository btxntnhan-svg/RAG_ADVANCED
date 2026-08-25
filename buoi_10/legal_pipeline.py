from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None


MODEL_NAME = "thuannc/vi-distilled-msmarco-MiniLM-L12-cos-v5"


def clean_html_content(html_text: str) -> str:
    """Làm sạch HTML nhưng vẫn giữ các heading, đoạn văn, bảng biểu."""
    if not html_text:
        return ""

    soup = BeautifulSoup(html_text, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "iframe", "header", "footer", "nav"]):
        tag.decompose()

    for table in soup.find_all("table"):
        rows: List[str] = []
        for row in table.find_all("tr"):
            cells = []
            for cell in row.find_all(["th", "td"]):
                value = " ".join(cell.get_text(" ", strip=True).split())
                if value:
                    cells.append(value)
            if cells:
                rows.append(" | ".join(cells))
        if rows:
            table.replace_with("\n".join(rows))

    fragments: List[str] = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "blockquote"]):
        text = " ".join(tag.get_text(" ", strip=True).split())
        if text and len(text) > 2:
            fragments.append(text)

    return "\n".join(fragments)


def _render_html_from_sections(spec: Dict[str, Any]) -> str:
    blocks: List[str] = [f"<h1>{spec['title']}</h1>"]
    for section in spec["sections"]:
        blocks.append(f"<h2>{section['title']}</h2>")
        for para in section["paragraphs"]:
            blocks.append(f"<p>{para}</p>")
    return "\n".join(blocks)


def build_sample_legal_documents() -> List[Dict[str, Any]]:
    """Tạo bộ dữ liệu mẫu với 15 tài liệu pháp lý giả lập."""
    specs = [
        {
            "doc_id": "DOC_001",
            "title": "Luật Hôn nhân và Gia đình",
            "year": 2014,
            "source": "Bộ Tư pháp",
            "category": "hôn_nhân",
            "sections": [
                {"title": "Chương I. Quy định chung", "paragraphs": ["Luật này quy định về hôn nhân, gia đình, quyền và nghĩa vụ của vợ chồng.", "Mục đích của pháp luật là bảo vệ quyền lợi của các thành viên trong gia đình."]},
                {"title": "Mục 1. Đăng ký kết hôn", "paragraphs": ["Công dân đủ điều kiện kết hôn phải nộp hồ sơ theo quy định của cơ quan nhà nước có thẩm quyền.", "Việc kết hôn được đăng ký tại UBND cấp xã nơi cư trú."]},
                {"title": "Điều 1. Khái niệm", "paragraphs": ["Hôn nhân là sự kết hợp giữa nam và nữ theo quy định của pháp luật.", "Hôn nhân được thực hiện trên nguyên tắc tự nguyện, bình đẳng và tiến bộ."]},
            ],
        },
        {
            "doc_id": "DOC_002",
            "title": "Luật Đất đai",
            "year": 2024,
            "source": "Chính phủ",
            "category": "đất_đai",
            "sections": [
                {"title": "Chương I. Về quyền sử dụng đất", "paragraphs": ["Đất đai do Nhà nước quản lý và giao cho tổ chức, cá nhân sử dụng theo quy định.", "Người sử dụng đất có quyền chuyển nhượng, cho thuê hoặc thế chấp đất đai nếu phù hợp với pháp luật."]},
                {"title": "Mục 1. Phân loại đất", "paragraphs": ["Đất nông nghiệp, đất ở, đất công nghiệp và đất chuyên dùng là các loại đất chính.", "Việc phân loại đất phải căn cứ vào mục đích sử dụng và quy hoạch của địa phương."]},
            ],
        },
        {
            "doc_id": "DOC_003",
            "title": "Luật Giao thông đường bộ",
            "year": 2022,
            "source": "Quốc hội",
            "category": "giao_thong",
            "sections": [
                {"title": "Chương I. Quy định chung", "paragraphs": ["Pháp luật này quy định về tổ chức, quản lý và điều khiển giao thông đường bộ.", "Mọi phương tiện tham gia giao thông phải tuân thủ biển báo và quy tắc an toàn."]},
                {"title": "Điều 1. Đường bộ", "paragraphs": ["Đường bộ là tuyến đường dành cho phương tiện và người tham gia giao thông.", "Đường bộ phải được thiết kế, xây dựng và bảo dưỡng theo tiêu chuẩn kỹ thuật."]},
            ],
        },
        {
            "doc_id": "DOC_004",
            "title": "Luật Kinh doanh bất động sản",
            "year": 2023,
            "source": "Bộ Xây dựng",
            "category": "bds",
            "sections": [
                {"title": "Chương I. Nội dung cơ bản", "paragraphs": ["Kinh doanh bất động sản phải tuân thủ các điều kiện về giấy phép, tài chính và thẩm định.", "Thị trường bất động sản phải minh bạch và công bằng để bảo vệ quyền lợi người mua."]},
                {"title": "Mục 1. Giao dịch", "paragraphs": ["Giao dịch bất động sản phải có hợp đồng bằng văn bản theo quy định.", "Các giao dịch không phù hợp pháp luật có thể bị hủy bỏ hoặc xử lý theo quy định."]},
            ],
        },
        {
            "doc_id": "DOC_005",
            "title": "Luật Thuế doanh nghiệp",
            "year": 2019,
            "source": "Bộ Tài chính",
            "category": "thuế",
            "sections": [
                {"title": "Chương I. Đối tượng chịu thuế", "paragraphs": ["Doanh nghiệp có thu nhập chịu thuế phải kê khai và nộp thuế theo quy định.", "Phân loại doanh nghiệp theo ngành nghề, quy mô và hình thức hoạt động."]},
                {"title": "Điều 1. Căn cứ tính thuế", "paragraphs": ["Căn cứ tính thuế là doanh thu, chi phí hợp lý và thu nhập chịu thuế.", "Điều chỉnh thuế phải theo quy định của luật hiện hành."]},
            ],
        },
        {
            "doc_id": "DOC_006",
            "title": "Luật Người lao động",
            "year": 2019,
            "source": "Bộ Lao động",
            "category": "lao_dong",
            "sections": [
                {"title": "Chương I. Quy định chung", "paragraphs": ["Người lao động có quyền làm việc trong điều kiện an toàn, lành mạnh và bình đẳng.", "Nghề nghiệp và nơi làm việc của người lao động phải bảo đảm quyền dân sự và lao động."]},
                {"title": "Mục 1. Hợp đồng lao động", "paragraphs": ["Hợp đồng lao động phải được ký kết theo nguyên tắc tự nguyện, minh bạch.", "Khi chấm dứt hợp đồng, doanh nghiệp phải thực hiện đầy đủ các nghĩa vụ theo quy định."]},
            ],
        },
        {
            "doc_id": "DOC_007",
            "title": "Luật An ninh mạng",
            "year": 2024,
            "source": "Bộ Thông tin và Truyền thông",
            "category": "an_ninh_mang",
            "sections": [
                {"title": "Chương I. Tổ chức quản lý", "paragraphs": ["An ninh mạng là nhiệm vụ quan trọng của cơ quan quản lý nhà nước và doanh nghiệp.", "Mọi tổ chức, cá nhân phải bảo vệ tài sản, dữ liệu và hệ thống thông tin."]},
                {"title": "Điều 1. Nền tảng an toàn", "paragraphs": ["Tổ chức, cá nhân phải xây dựng chính sách an toàn thông tin phù hợp.", "Đảm bảo dữ liệu và tài sản kỹ thuật số được bảo vệ trước tấn công mạng."]},
            ],
        },
        {
            "doc_id": "DOC_008",
            "title": "Luật Bảo vệ môi trường",
            "year": 2020,
            "source": "Bộ Tài nguyên và Môi trường",
            "category": "moi_truong",
            "sections": [
                {"title": "Chương I. Nguyên tắc chung", "paragraphs": ["Môi trường là tài nguyên quý giá cần được bảo vệ, sử dụng bền vững.", "Tổ chức và cá nhân phải thực hiện nghĩa vụ bảo vệ môi trường trong mọi hoạt động của mình."]},
                {"title": "Mục 1. Ô nhiễm và suy thoái", "paragraphs": ["Ô nhiễm môi trường phải được kiểm soát và xử lý theo quy trình kỹ thuật, pháp lý.", "Mọi hành vi gây ô nhiễm nặng có thể bị xử phạt theo mức độ vi phạm."]},
            ],
        },
        {
            "doc_id": "DOC_009",
            "title": "Luật Doanh nghiệp",
            "year": 2020,
            "source": "Bộ Kế hoạch và Đầu tư",
            "category": "doanh_nghiep",
            "sections": [
                {"title": "Chương I. Hình thức doanh nghiệp", "paragraphs": ["Doanh nghiệp có thể hoạt động dưới các hình thức công ty cổ phần, TNHH, hợp danh hoặc cá nhân kinh doanh.", "Quy định về thành lập và hoạt động phải đảm bảo tính công khai, minh bạch."]},
                {"title": "Điều 1. Chứng nhận thành lập", "paragraphs": ["Doanh nghiệp phải hoàn tất thủ tục đăng ký kinh doanh trước khi bắt đầu hoạt động.", "Cơ quan nhà nước cấp giấy chứng nhận theo quy định hiện hành."]},
            ],
        },
        {
            "doc_id": "DOC_010",
            "title": "Luật Trật tự an toàn giao thông",
            "year": 2022,
            "source": "Cục CSGT",
            "category": "an_toan_giao_thong",
            "sections": [
                {"title": "Chương I. Nguyên tắc", "paragraphs": ["Người tham gia giao thông phải tuân thủ tín hiệu, biển báo và đường đi phải được ưu tiên.", "Tổ chức, cá nhân không được sử dụng phương tiện khi không đủ điều kiện pháp lý."]},
                {"title": "Mục 1. Xử lý vi phạm", "paragraphs": ["Hành vi vi phạm giao thông phải được xử lý kịp thời, công bằng và có tính răn đe.", "Việc xử lý vi phạm phải tuân thủ quy định về hồ sơ, tài liệu và căn cứ pháp lý."]},
            ],
        },
        {
            "doc_id": "DOC_011",
            "title": "Luật Tiêu chuẩn chất lượng",
            "year": 2021,
            "source": "Bộ Khoa học và Công nghệ",
            "category": "chat_luong",
            "sections": [
                {"title": "Chương I. Quy định chung", "paragraphs": ["Sản phẩm, dịch vụ phải đáp ứng tiêu chuẩn chất lượng theo quy định của thị trường và pháp luật.", "Tổ chức và cá nhân phải chứng minh chất lượng thông qua kiểm định và đánh giá."]},
                {"title": "Mục 1. Kiểm định", "paragraphs": ["Kiểm định chất lượng được thực hiện bởi cơ quan hoặc tổ chức có thẩm quyền.", "Kết quả kiểm định phải được lưu trữ và công bố theo quy định."]},
            ],
        },
        {
            "doc_id": "DOC_012",
            "title": "Luật Điện lực",
            "year": 2022,
            "source": "Bộ Công thương",
            "category": "dien_luc",
            "sections": [
                {"title": "Chương I. Nguyên tắc quản lý", "paragraphs": ["Hoạt động điện lực phải đảm bảo an toàn, tiết kiệm và hiệu quả.", "Nhà nước quản lý chặt chẽ việc đầu tư, xây dựng và vận hành hệ thống điện."]},
                {"title": "Điều 1. Sản xuất và phân phối", "paragraphs": ["Sản xuất, truyền tải và phân phối điện phải tuân thủ tiêu chuẩn kỹ thuật quốc gia.", "Mọi sự cố điện cần được khắc phục nhanh và an toàn."]},
            ],
        },
        {
            "doc_id": "DOC_013",
            "title": "Luật Y tế",
            "year": 2023,
            "source": "Bộ Y tế",
            "category": "y_te",
            "sections": [
                {"title": "Chương I. Bảo vệ sức khỏe cộng đồng", "paragraphs": ["Công tác y tế phải bảo đảm tính công bằng, hiệu quả và quyền lợi người bệnh.", "Hệ thống y tế phải liên tục nâng cao chất lượng dịch vụ và điều kiện làm việc."]},
                {"title": "Mục 1. Bệnh viện và cơ sở y tế", "paragraphs": ["Cơ sở y tế phải tuân thủ quy định về quản lý, kỹ thuật và chăm sóc người bệnh.", "Việc cấp phép, hoạt động và kiểm định được thực hiện theo quy định pháp luật."]},
            ],
        },
        {
            "doc_id": "DOC_014",
            "title": "Luật Đầu tư",
            "year": 2023,
            "source": "Bộ Kế hoạch và Đầu tư",
            "category": "dau_tu",
            "sections": [
                {"title": "Chương I. Nguyên tắc đầu tư", "paragraphs": ["Đầu tư phải dựa trên nguyên tắc hiệu quả, công bằng, minh bạch và bền vững.", "Các dự án đầu tư phải phù hợp với quy hoạch và bảo vệ môi trường."]},
                {"title": "Mục 1. Hình thức đầu tư", "paragraphs": ["Đầu tư có thể thực hiện ở trong nước, nước ngoài và theo hình thức hợp tác.", "Các dự án đầu tư phải có kế hoạch, nguồn vốn và phương án quản lý rõ ràng."]},
            ],
        },
        {
            "doc_id": "DOC_015",
            "title": "Luật Dân sự",
            "year": 2015,
            "source": "Quốc hội",
            "category": "dan_su",
            "sections": [
                {"title": "Chương I. Quyền và nghĩa vụ", "paragraphs": ["Công dân có quyền tự do, bình đẳng trong các quan hệ dân sự.", "Mọi cá nhân, tổ chức phải thực hiện nghĩa vụ dân sự theo quy định pháp luật."]},
                {"title": "Điều 1. Căn cứ pháp lý", "paragraphs": ["Quan hệ dân sự phát sinh từ hợp đồng, hành vi pháp lý, thừa kế hoặc khác.", "Pháp luật về dân sự giữ vai trò quan trọng trong đời sống xã hội và kinh tế."]},
            ],
        },
    ]

    docs: List[Dict[str, Any]] = []
    for spec in specs:
        html = _render_html_from_sections(spec)
        docs.append({
            "doc_id": spec["doc_id"],
            "title": spec["title"],
            "year": spec["year"],
            "source": spec["source"],
            "category": spec["category"],
            "html": html,
        })
    return docs


def build_hierarchy_chunks(document: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Phân tách HTML thành các chunk có cấu trúc cha-con."""
    html_text = document.get("html", "")
    if not html_text:
        return []
    
    # Parse HTML trực tiếp (không clean trước)
    soup = BeautifulSoup(html_text, "html.parser")
    
    # Loại bỏ các tag không cần thiết
    for tag in soup(["script", "style", "noscript", "svg", "iframe", "header", "footer", "nav"]):
        tag.decompose()

    sections: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None

    def flush_current() -> None:
        nonlocal current
        if current is not None:
            text_value = " ".join(current["parts"]).strip()
            if text_value:
                current["text"] = text_value
                sections.append(current)
            current = None

    # Duyệt qua các tag h1, h2, h3, h4, p, li, blockquote (giữ lại structure)
    for node in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "blockquote"]):
        if node.name in {"h1", "h2", "h3", "h4"}:
            flush_current()
            current = {
                "title": node.get_text(" ", strip=True),
                "level": int(node.name[1]),
                "parts": [],
                "doc_id": document["doc_id"],
            }
        else:
            if current is not None:
                value = " ".join(node.get_text(" ", strip=True).split())
                if value and len(value) > 2:
                    current["parts"].append(value)

    flush_current()

    chunk_records: List[Dict[str, Any]] = []
    stack: Dict[int, Dict[str, Any]] = {}
    for idx, section in enumerate(sections):
        chunk_id = f"{document['doc_id']}_CHUNK_{idx + 1}"
        parent_id = None
        for higher_level in range(section["level"] - 1, 0, -1):
            parent_candidate = stack.get(higher_level)
            if parent_candidate is not None:
                parent_id = parent_candidate["chunk_id"]
                break

        chunk_record = {
            "chunk_id": chunk_id,
            "doc_id": document["doc_id"],
            "title": section["title"],
            "level": section["level"],
            "text": section.get("text", " ".join(section["parts"])),
            "parent_id": parent_id,
            "source_title": document["title"],
        }
        chunk_records.append(chunk_record)
        stack[section["level"]] = chunk_record

    for parent_id in {chunk["parent_id"] for chunk in chunk_records if chunk["parent_id"] is not None}:
        siblings = [chunk for chunk in chunk_records if chunk["parent_id"] == parent_id]
        for i in range(len(siblings) - 1):
            siblings[i]["next_chunk_id"] = siblings[i + 1]["chunk_id"]

    return chunk_records


def print_sample_chunks(chunks: List[Dict[str, Any]], limit: int = 6) -> str:
    lines: List[str] = []
    lines.append("=== SAMPLE CHUNKING OUTPUT ===")
    for chunk in chunks[:limit]:
        parent = chunk.get("parent_id")
        lines.append(f"- {chunk['chunk_id']} | level={chunk['level']} | parent={parent} | title={chunk['title']}")
        preview = chunk["text"][:180].replace("\n", " ")
        lines.append(f"  {preview}...")
    return "\n".join(lines)


def build_embedding_model(model_name: str = MODEL_NAME):
    if SentenceTransformer is None:
        return None
    try:
        return SentenceTransformer(model_name, device="cpu")
    except Exception:
        return None


def generate_embeddings(chunks: List[Dict[str, Any]], model) -> List[List[float]]:
    if model is None or not chunks:
        return [[0.0] * 384 for _ in chunks]
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=False)
    return embeddings.tolist()


def build_document_edges() -> List[Tuple[str, str, str]]:
    return [
        ("DOC_001", "DOC_002", "THAY_THE"),
        ("DOC_001", "DOC_003", "CAN_CU"),
        ("DOC_002", "DOC_004", "HOP_NHAT"),
        ("DOC_005", "DOC_006", "CAN_CU"),
        ("DOC_006", "DOC_007", "THAY_THE"),
        ("DOC_007", "DOC_008", "CAN_CU"),
        ("DOC_003", "DOC_009", "HOP_NHAT"),
        ("DOC_010", "DOC_011", "THAY_THE"),
    ]


def convert_document_to_neo4j_record(document: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "doc_id": document["doc_id"],
        "title": document["title"],
        "source": document["source"],
        "year": document["year"],
        "category": document["category"],
    }


def test_neo4j_connection(driver) -> Tuple[bool, str]:
    """Kiểm tra kết nối Neo4j có hoạt động bình thường.
    
    Returns:
        (success: bool, message: str)
    """
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            result.single()
        return True, "✅ Kết nối Neo4j thành công"
    except Exception as e:
        return False, f"❌ Kết nối Neo4j thất bại: {str(e)}"


def setup_database(driver, database_name: str = "kb-hops", clear_data: bool = True) -> Tuple[bool, str]:
    """Tạo database mới hoặc làm sạch dữ liệu cũ.
    
    Args:
        driver: Neo4j driver
        database_name: Tên database (mặc định: kb-hops)
        clear_data: Xóa dữ liệu cũ hay không (mặc định: True)
    
    Returns:
        (success: bool, message: str)
    """
    try:
        # Bước 1: Kiểm tra database có tồn tại không
        with driver.session(database="system") as session:
            result = session.run(f"SHOW DATABASES WHERE name = '{database_name}'")
            db_exists = result.single() is not None
        
        # Bước 2: Nếu chưa tồn tại, tạo database (bọc tên trong backtick nếu có dấu đặc biệt)
        if not db_exists:
            with driver.session(database="system") as session:
                # Dùng backtick để bọc database name nếu chứa dấu -
                quoted_name = f"`{database_name}`" if "-" in database_name else database_name
                session.run(f"CREATE DATABASE {quoted_name} IF NOT EXISTS")
            msg = f"✅ Database '{database_name}' được tạo thành công"
        else:
            msg = f"ℹ️ Database '{database_name}' đã tồn tại"
        
        # Bước 3: Xóa dữ liệu cũ nếu clear_data=True
        if clear_data:
            try:
                with driver.session(database=database_name) as session:
                    session.run("MATCH (n) DETACH DELETE n")
                msg += " và được làm sạch"
            except Exception as e:
                # Nếu database chưa sẵn sàng, hãy thử lại
                import time
                time.sleep(1)  # Chờ 1 giây database khởi động
                try:
                    with driver.session(database=database_name) as session:
                        session.run("MATCH (n) DETACH DELETE n")
                    msg += " và được làm sạch (sau khi chờ)"
                except Exception as retry_error:
                    msg += f"\n⚠️ Không thể làm sạch dữ liệu: {str(retry_error)}"
        
        return True, msg
    except Exception as e:
        error_msg = str(e)
        if "DatabaseNotFound" in error_msg or "does not exist" in error_msg:
            return False, (
                f"❌ Database '{database_name}' không tồn tại\n\n"
                f"💡 Hướng dẫn cách khắc phục:\n"
                f"1. Mở Neo4j Desktop\n"
                f"2. Tạo một instance mới (hoặc chọn instance hiện tại)\n"
                f"3. Bấm nút 'Start' để khởi động instance\n"
                f"4. Chờ khoảng 10-15 giây cho database khởi động\n"
                f"5. Quay lại app và bấy nút 'Setup Database' lại\n\n"
                f"Lỗi chi tiết: {error_msg}"
            )
        else:
            return False, f"❌ Lỗi setup database: {error_msg}"


def verify_neo4j_counts(driver, database: str = "kb-hops") -> Dict[str, Any]:
    """Kiểm tra và xác minh số lượng nodes và relationships.
    
    Xác minh:
    - 15 Document nodes
    - 8 Document relationships (CAN_CU, THAY_THE, HOP_NHAT)
    - Chunk nodes, PART_OF, PARENT_OF, NEXT relationships
    """
    with driver.session(database=database) as session:
        # Document level
        doc_count = session.run("MATCH (d:Document) RETURN count(d) AS count").single()["count"]
        doc_rel_count = session.run("MATCH (:Document)-[r]->(:Document) RETURN count(r) AS count").single()["count"]
        
        # Chunk level
        chunk_count = session.run("MATCH (c:Chunk) RETURN count(c) AS count").single()["count"]
        part_of_count = session.run("MATCH (:Chunk)-[:PART_OF]->(:Document) RETURN count(*) AS count").single()["count"]
        parent_of_count = session.run("MATCH (:Chunk)-[:PARENT_OF]->(:Chunk) RETURN count(*) AS count").single()["count"]
        next_count = session.run("MATCH (:Chunk)-[:NEXT]->(:Chunk) RETURN count(*) AS count").single()["count"]
        
        # Document edge types
        can_cu_count = session.run("MATCH ()-[:CAN_CU]->() RETURN count(*) AS count").single()["count"]
        thay_the_count = session.run("MATCH ()-[:THAY_THE]->() RETURN count(*) AS count").single()["count"]
        hop_nhat_count = session.run("MATCH ()-[:HOP_NHAT]->() RETURN count(*) AS count").single()["count"]
    
    return {
        "document_count": int(doc_count),
        "document_relation_count": int(doc_rel_count),
        "chunk_count": int(chunk_count),
        "part_of_count": int(part_of_count),
        "parent_of_count": int(parent_of_count),
        "next_relation_count": int(next_count),
        "document_edges": {
            "CAN_CU": int(can_cu_count),
            "THAY_THE": int(thay_the_count),
            "HOP_NHAT": int(hop_nhat_count),
        },
    }
