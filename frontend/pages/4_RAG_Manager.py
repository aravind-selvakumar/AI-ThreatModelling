import streamlit as st

from utils.api_client import (
    delete_document,
    get_ingestion_stats,
    list_documents,
    reindex_documents,
    upload_document,
)

st.set_page_config(page_title="RAG Manager - ThreatModellingEngine", page_icon="🛡️", layout="wide")

if "token" not in st.session_state:
    st.switch_page("app.py")

role = st.session_state.get("role", "guest")
if role != "admin":
    st.error("Access denied. Admin privileges required.")
    st.stop()

token = st.session_state.token

st.title("📚 RAG Knowledge Base Manager")
st.markdown("Upload, manage, and re-index organizational security standards.")

stats = get_ingestion_stats(token)
col1, col2 = st.columns(2)
col1.metric("Documents", stats.get("documents", 0))
col2.metric("Vector Chunks", stats.get("chunks", 0))

st.divider()

tab1, tab2, tab3 = st.tabs(["Upload Documents", "View Documents", "Re-Index"])

with tab1:
    uploaded_files = st.file_uploader(
        "Upload security standards or policy documents",
        type=["pdf", "md", "txt"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        for f in uploaded_files:
            st.write(f"📄 **{f.name}** ({(len(f.getvalue()) / 1024):.1f} KB)")
        if st.button("🚀 Ingest All", type="primary", use_container_width=True):
            progress = st.progress(0, text="Uploading...")
            results = []
            for i, f in enumerate(uploaded_files):
                result = upload_document(token, f.getvalue(), f.name)
                if result:
                    results.append(result)
                    st.success(f"✅ {f.name}: {result['chunk_count']} chunks ingested")
                else:
                    st.error(f"❌ Failed to ingest {f.name}")
                progress.progress((i + 1) / len(uploaded_files), text=f"{i+1}/{len(uploaded_files)} completed")
            st.rerun()

with tab2:
    docs = list_documents(token)
    if docs:
        for doc in docs:
            with st.container(border=True):
                cols = st.columns([3, 1, 1, 1])
                cols[0].write(f"**{doc['title']}**")
                cols[1].write(f"`{doc['doc_type']}`")
                cols[2].write(doc["created_at"][:10])
                if cols[3].button("Delete", key=f"del_{doc['id']}"):
                    if delete_document(token, doc["id"]):
                        st.success(f"Deleted {doc['title']}")
                        st.rerun()
                    else:
                        st.error("Delete failed")
    else:
        st.info("No documents in the knowledge base. Upload documents to populate.")

with tab3:
    st.warning("Re-indexing re-processes all documents into the vector store.")
    if st.button("🔄 Re-Index All Documents", type="primary", use_container_width=True):
        with st.spinner("Re-indexing..."):
            result = reindex_documents(token)
            if result:
                st.success(f"Re-indexed {result['chunk_count']} chunks")
                st.rerun()
            else:
                st.error("Re-index failed")

st.divider()

if st.button("← Back to Dashboard"):
    st.switch_page("pages/1_Dashboard.py")
