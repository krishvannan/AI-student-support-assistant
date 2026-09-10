"""
AI College Assistant (RAG) Page for CampusAI.
Provides interactive conversational Q&A with document citations, PDF upload, and student memory personalization.
"""

import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.retriever import CollegeAssistantRAG
from rag.loader import PDFDocumentLoader
from rag.splitter import DocumentSplitter
from rag.vectorstore import get_vector_store
from memory.student_memory import StudentMemory
from database.sqlite_db import get_chat_history, clear_chat_history
from utils.config import DOCUMENTS_DIR
from utils.helpers import setup_page


def main():
    setup_page(
        title="AI College Assistant",
        subtitle="Ask questions about university policies, syllabus, exam timetables, and notices",
        icon="💬"
    )

    profile = StudentMemory.get_profile()
    vector_store = get_vector_store()
    rag_engine = CollegeAssistantRAG(session_id="student_session")

    # Top Control Bar: Document Drawer & Memory Toggle
    with st.expander("📂 Document Management & Settings", expanded=False):
        c1, c2 = st.columns([1, 1])

        with c1:
            st.markdown("#### 📤 Upload New College PDFs")
            uploaded_files = st.file_uploader(
                "Upload circulars, syllabus, or regulations (PDF)",
                type=["pdf"],
                accept_multiple_files=True,
                key="chat_pdf_uploader"
            )

            if uploaded_files and st.button("Index Uploaded PDFs", key="btn_index_uploaded"):
                with st.spinner("Processing and indexing documents into ChromaDB..."):
                    total_chunks = 0
                    splitter = DocumentSplitter(chunk_size=750, chunk_overlap=120)
                    for up_file in uploaded_files:
                        docs = PDFDocumentLoader.load_from_bytes(up_file.read(), up_file.name)
                        chunks = splitter.split_documents(docs)
                        added = vector_store.add_documents(chunks)
                        total_chunks += added

                    st.success(f"Successfully processed and indexed {total_chunks} chunks into ChromaDB!")
                    st.rerun()

        with c2:
            st.markdown("#### 🗄️ Knowledge Base Status")
            indexed_docs = vector_store.get_indexed_files()
            chunk_count = vector_store.get_document_count()

            st.metric("Total Indexed Chunks", chunk_count)
            if indexed_docs:
                st.write("**Indexed Documents:**")
                for doc in indexed_docs:
                    st.markdown(f"- 📄 `{doc}`")
            else:
                st.warning("No documents currently indexed in ChromaDB.")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📥 Index Sample PDFs", key="btn_load_samples"):
                    with st.spinner("Loading sample university PDFs from documents/ ..."):
                        docs = PDFDocumentLoader.load_directory(str(DOCUMENTS_DIR))
                        if docs:
                            splitter = DocumentSplitter(chunk_size=750, chunk_overlap=120)
                            chunks = splitter.split_documents(docs)
                            added = vector_store.add_documents(chunks)
                            st.success(f"Indexed {added} chunks from {len(docs)} sample document pages!")
                            st.rerun()
                        else:
                            st.error("No sample PDFs found in documents/ directory.")

            with col_btn2:
                if st.button("🗑️ Reset Vector Store", key="btn_clear_vs"):
                    vector_store.clear()
                    st.success("Vector store cleared!")
                    st.rerun()

    # Personalization and Options Bar
    col_opt1, col_opt2, col_opt3 = st.columns([2, 1, 1])
    with col_opt1:
        use_profile = st.checkbox(
            f"🧠 Use Student Profile Memory ({profile.name}, Sem {profile.semester} {profile.department})",
            value=True,
            help="Personalizes responses using your enrolled department, semester, and subjects"
        )
    with col_opt2:
        top_k = st.slider("Context Chunks", min_value=2, max_value=8, value=4, help="Number of chunks retrieved from ChromaDB")
    with col_opt3:
        if st.button("🧹 Clear Chat", use_container_width=True):
            clear_chat_history("student_session")
            st.rerun()

    # Quick Suggestion Chips
    st.markdown("##### 💡 Suggested Questions")
    chip_cols = st.columns(4)
    suggested_q = None

    with chip_cols[0]:
        if st.button("📋 Attendance Rule?", key="q1", use_container_width=True):
            suggested_q = "What is the minimum attendance requirement and what happens if a student has less than 65%?"
    with chip_cols[1]:
        if st.button("💼 Placement Drive?", key="q2", use_container_width=True):
            suggested_q = "What is the eligibility criteria and deadline for the Mega Placement Drive?"
    with chip_cols[2]:
        if st.button("📚 My Semester Syllabus?", key="q3", use_container_width=True):
            suggested_q = "What subjects should I prioritize and what are the main units in my curriculum?"
    with chip_cols[3]:
        if st.button("⏰ Exam Timetable?", key="q4", use_container_width=True):
            suggested_q = "When is the deadline to pay exam fees without fine and when do theory exams start?"

    # Display Chat History from SQLite
    st.markdown("---")
    history = get_chat_history("student_session", limit=50)

    for msg in history:
        if msg.sender == "user":
            with st.chat_message("user", avatar="🎓"):
                st.markdown(msg.message)
        else:
            with st.chat_message("assistant", avatar="🏛️"):
                st.markdown(msg.message)
                if msg.sources:
                    with st.expander(f"📚 Verified Sources ({len(msg.sources)} references)"):
                        for s in msg.sources:
                            st.markdown(
                                f"""
                                <div class="source-citation-card">
                                    <div class="source-title">📄 {s.get('source')} (Page {s.get('page')})</div>
                                    <div class="source-excerpt">"{s.get('snippet')}"</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

    # Chat Input Handling
    user_input = st.chat_input("Ask about college regulations, exam fees, syllabus, or placement drives...")

    final_query = suggested_q or user_input

    if final_query:
        # Display user message immediately
        with st.chat_message("user", avatar="🎓"):
            st.markdown(final_query)

        # Process with RAG Assistant
        with st.chat_message("assistant", avatar="🏛️"):
            with st.spinner("Searching college knowledge base and generating answer..."):
                response = rag_engine.query(
                    user_question=final_query,
                    k=top_k,
                    use_memory=True,
                    use_student_profile=use_profile
                )
                st.markdown(response["answer"])

                if response.get("sources"):
                    with st.expander(f"📚 Verified Sources ({len(response['sources'])} references)"):
                        for s in response["sources"]:
                            st.markdown(
                                f"""
                                <div class="source-citation-card">
                                    <div class="source-title">📄 {s.get('source')} (Page {s.get('page')})</div>
                                    <div class="source-excerpt">"{s.get('snippet')}"</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

        st.rerun()


if __name__ == "__main__" or True:
    main()
