import os
import json
from datetime import datetime
from typing import List, Dict, Any

import streamlit as st
import pandas as pd


DATA_FILE = "documents_meta.json"
UPLOAD_DIR = "uploaded_documents"


def format_date_vn(date_str: str) -> str:
    """Chuyển đổi từ YYYY-MM-DD sang DD/MM/YYYY."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return date_str


def ensure_storage() -> None:
    """Ensure upload directory and metadata file exist."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def load_documents() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_documents(docs: List[Dict[str, Any]]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)


def add_document(file, title: str, category: str, doc_number: str, issue_date: str, receiver_sender: str, description: str, tags: List[str]) -> None:
    ensure_storage()
    docs = load_documents()

    safe_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{file.name}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as out:
        out.write(file.getbuffer())

    doc = {
        "id": safe_name,
        "file_name": file.name,
        "stored_name": safe_name,
        "path": file_path,
        "title": title or file.name,
        "category": category,
        "doc_number": doc_number,
        "issue_date": issue_date, # Lưu dạng YYYY-MM-DD để dễ lọc
        "receiver_sender": receiver_sender,
        "description": description,
        "tags": [t.strip() for t in tags if t.strip()],
        "uploaded_at": datetime.now().isoformat(timespec="seconds"),
        "size_bytes": file.size,
    }
    docs.append(doc)
    save_documents(docs)


def delete_document(doc_id: str) -> None:
    docs = load_documents()
    remaining: List[Dict[str, Any]] = []
    to_delete = None

    for d in docs:
        if d["id"] == doc_id:
            to_delete = d
        else:
            remaining.append(d)

    if to_delete:
        if os.path.exists(to_delete["path"]):
            try:
                os.remove(to_delete["path"])
            except OSError:
                pass

    save_documents(remaining)


def filter_documents(
    docs: List[Dict[str, Any]], keyword: str, category_filter: str, tag_filter: str, date_range: tuple = None
) -> List[Dict[str, Any]]:
    keyword = (keyword or "").lower().strip()
    category_filter = (category_filter or "").strip()
    tag_filter = (tag_filter or "").lower().strip()

    filtered = []
    for d in docs:
        ok = True

        if category_filter and d.get("category") != category_filter:
            ok = False

        if ok and date_range and len(date_range) == 2:
            try:
                doc_date = datetime.strptime(d.get("issue_date", ""), "%Y-%m-%d").date()
                if not (date_range[0] <= doc_date <= date_range[1]):
                    ok = False
            except ValueError:
                pass

        if ok and keyword:
            haystack = " ".join(
                [
                    d.get("title", ""),
                    d.get("doc_number", ""),
                    d.get("receiver_sender", ""),
                    d.get("description", ""),
                    d.get("file_name", ""),
                    " ".join(d.get("tags", [])),
                ]
            ).lower()
            if keyword not in haystack:
                ok = False

        if ok and tag_filter:
            tags_lower = [t.lower() for t in d.get("tags", [])]
            if tag_filter not in tags_lower:
                ok = False

        if ok:
            filtered.append(d)

    return filtered


def sidebar_upload():
    st.sidebar.header("Tải lên văn bản")
    file = st.sidebar.file_uploader("Chọn tệp văn bản", type=None)
    
    category = st.sidebar.radio("Loại văn bản", ["Văn bản Đến", "Văn bản Đi"])
    
    title = st.sidebar.text_input("Trích yếu/Tiêu đề")
    doc_number = st.sidebar.text_input("Số/Ký hiệu")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        issue_date = st.sidebar.date_input("Ngày ban hành/đến", format="DD/MM/YYYY")
    with col2:
        label = "Nơi gửi" if category == "Văn bản Đến" else "Nơi nhận"
        receiver_sender = st.sidebar.text_input(label)
            
    description = st.sidebar.text_area("Ghi chú")
    tags_raw = st.sidebar.text_input("Từ khóa (cách nhau bởi dấu phẩy)")

    if st.sidebar.button("Lưu văn bản") and file is not None:
        tags = tags_raw.split(",") if tags_raw else []
        add_document(
            file, title, category, doc_number, str(issue_date), receiver_sender, description, tags
        )
        st.sidebar.success(f"Đã lưu {category} thành công!")
        st.rerun()


def render_stats(docs: List[Dict[str, Any]]):
    st.subheader("📊 Thống kê & Báo cáo")
    
    if not docs:
        st.info("Chưa có dữ liệu để thống kê.")
        return

    df = pd.DataFrame(docs)
    
    # Tổng quan
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng số văn bản", len(df))
    col2.metric("Văn bản Đến", len(df[df['category'] == 'Văn bản Đến']))
    col3.metric("Văn bản Đi", len(df[df['category'] == 'Văn bản Đi']))

    st.markdown("---")
    
    # Biểu đồ xu hướng
    st.write("**Số lượng văn bản theo thời gian (Ngày ban hành)**")
    df['issue_date'] = pd.to_datetime(df['issue_date'])
    date_counts = df.groupby(['issue_date', 'category']).size().unstack(fill_value=0)
    st.line_chart(date_counts)

    # Xuất báo cáo
    st.markdown("---")
    st.write("**Xuất báo cáo danh sách văn bản**")
    
    export_df = df[['category', 'doc_number', 'issue_date', 'title', 'receiver_sender', 'uploaded_at']].copy()
    export_df.columns = ['Loại', 'Số/Ký hiệu', 'Ngày ban hành', 'Trích yếu', 'Nơi gửi/nhận', 'Ngày upload']
    export_df['Ngày ban hành'] = export_df['Ngày ban hành'].dt.strftime('%d/%m/%Y')
    
    csv = export_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Tải báo cáo CSV (Excel)",
        data=csv,
        file_name=f"bao_cao_van_ban_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


def render_document_list():
    docs = load_documents()

    # Tabs chính luôn hiển thị để người dùng thấy các tính năng
    tab_list, tab_stats = st.tabs(["📋 Danh sách văn bản", "📊 Thống kê & Báo cáo"])
    
    with tab_list:
        if not docs:
            st.info("Chưa có văn bản nào. Hãy tải lên ở thanh bên trái.")
        else:
            # Bộ lọc nâng cao
            with st.expander("🔍 Tìm kiếm & Lọc nâng cao", expanded=False):
                col_k, col_d, col_t = st.columns([2, 2, 1])
                with col_k:
                    keyword = st.text_input("Tìm kiếm (số ký hiệu, tiêu đề, nội dung...)", key="search_main")
                with col_d:
                    date_range = st.date_input("Khoảng ngày ban hành", value=[], format="DD/MM/YYYY")
                with col_t:
                    all_tags = sorted({t for d in docs for t in d.get("tags", []) if isinstance(t, str)})
                    tag_filter = st.selectbox("Lọc từ khóa", options=[""] + all_tags, format_func=lambda x: x or "— Tất cả —")

            # Sub-tabs cho loại văn bản
            sub_tab1, sub_tab2 = st.tabs(["📂 Văn bản Đến", "📤 Văn bản Đi"])

            def display_docs(filtered_docs):
                if not filtered_docs:
                    st.warning("Không tìm thấy văn bản phù hợp.")
                    return

                for doc in sorted(filtered_docs, key=lambda d: d.get("uploaded_at", ""), reverse=True):
                    with st.expander(f"[{doc.get('doc_number', 'N/A')}] {doc['title']}"):
                        col_info, col_preview = st.columns([1, 1])
                        with col_info:
                            st.markdown(f"**Số/Ký hiệu:** {doc.get('doc_number', '—')}")
                            st.markdown(f"**Ngày ban hành/đến:** {format_date_vn(doc.get('issue_date', ''))}")
                            label = "Nơi gửi" if doc.get("category") == "Văn bản Đến" else "Nơi nhận"
                            st.markdown(f"**{label}:** {doc.get('receiver_sender', '—')}")
                            st.markdown(f"**Ghi chú:** {doc.get('description', '') or '—'}")
                            st.markdown(f"**Thời gian tải lên:** {doc.get('uploaded_at', '')}")

                            if os.path.exists(doc["path"]):
                                with open(doc["path"], "rb") as f:
                                    data = f.read()
                                st.download_button("📥 Tải xuống tệp", data=data, file_name=doc["file_name"], key=f"dl_{doc['id']}")
                            
                            if st.button("🗑️ Xóa văn bản", key=f"del_{doc['id']}"):
                                delete_document(doc["id"])
                                st.rerun()

                        with col_preview:
                            ext = os.path.splitext(doc["file_name"])[1].lower()
                            if os.path.exists(doc["path"]):
                                if ext in [".txt", ".md"]:
                                    with open(doc["path"], "rb") as f:
                                        st.text_area("Nội dung", f.read().decode("utf-8", errors="ignore"), height=250, key=f"text_{doc['id']}")
                                elif ext in [".png", ".jpg", ".jpeg", ".gif"]:
                                    st.image(doc["path"])
                                else:
                                    st.info("Bản xem trước không khả dụng.")

            with sub_tab1:
                filtered_den = filter_documents(docs, keyword, "Văn bản Đến", tag_filter, date_range)
                display_docs(filtered_den)

            with sub_tab2:
                filtered_di = filter_documents(docs, keyword, "Văn bản Đi", tag_filter, date_range)
                display_docs(filtered_di)

    with tab_stats:
        render_stats(docs)



def main():
    st.set_page_config(page_title="Quản lý Văn bản", layout="wide")
    st.title("📑 Phần mềm Quản lý Văn bản Đến và Đi")

    ensure_storage()
    sidebar_upload()
    render_document_list()


if __name__ == "__main__":
    main()


