"""
About Page for CampusAI.
Presents architecture documentation, tech stack breakdown, and viva presentation notes for college examiners.
"""

import streamlit as st
from utils.helpers import render_header, load_css


def render_about_page():
    """Render the About & Project Viva Guide page."""
    load_css()

    render_header(
        title="About CampusAI Project",
        subtitle="System architecture, technological framework, and college project viva documentation",
        icon="ℹ️"
    )

    st.markdown("### 🏛️ System Architecture")
    st.markdown(
        """
```
+---------------------------------------------------------------------------------------+
|                                    Streamlit Frontend                                 |
|   [Home]  |  [Ask Assistant (RAG)]  |  [Study Planner]  |  [Quiz Generator]  | [Profile] |
+---------------------------------------------------------------------------------------+
                                           │
                                           ▼
+───────────────────────────────────────────────────────────────────────────────────────+
|                                  LangChain Orchestration Layer                         |
|  - RAG Retriever Pipeline             - Dynamic System Prompts (Student Memory)        |
|  - RecursiveCharacterTextSplitter     - Few-Shot Reasoning & Output Parsers           |
+──────────────────────────────────────────┬────────────────────────────────────────────+
                     │                     │                     │
                     ▼                     ▼                     ▼
          ┌─────────────────────┐┌─────────────────────┐┌────────────────────────┐
          │    ChromaDB (VDB)   ││   SQLite Database   ││   Google Gemini API    │
          │  - PDF Page Chunks  ││  - Student Profiles ││  - gemini-1.5-flash    │
          │  - Gemini Embeddings││  - Chat History     ││  - text-embedding-004  │
          │  - Cosine Search    ││  - Saved Plans & Quiz││  - Tool Invocation     │
          └─────────────────────┘└─────────────────────┘└────────────────────────┘
```
        """
    )

    st.markdown("### 🛠️ Technology Stack Breakdown")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            - **Frontend Framework**: Streamlit (Responsive web interface with university styling)
            - **AI Framework**: LangChain (RAG pipeline, prompt templates, retrieval chains)
            - **Large Language Model**: Google Gemini API (`gemini-1.5-flash` / `gemini-1.5-pro`)
            - **Text Embeddings**: Google `text-embedding-004` (768-dimensional dense vectors)
            """
        )
    with col2:
        st.markdown(
            """
            - **Vector Database**: ChromaDB (Persistent local vector store with cosine similarity)
            - **Relational Database**: SQLite (Thread-safe storage for student profiles, history, and assessments)
            - **Document Ingestion**: PyPDF2 & pypdf (Page-level text extraction with source tracking)
            - **Configuration**: python-dotenv (Secure environment variable management)
            """
        )

    st.markdown("---")
    st.markdown("### 🎓 Viva & Project Examination Q&A Guide")

    with st.expander("Q1: Why is Retrieval-Augmented Generation (RAG) used instead of fine-tuning?"):
        st.markdown(
            """
            - **Freshness & Dynamism**: College circulars, exam dates, and regulations change frequently. RAG allows instant updates by simply uploading a new PDF without expensive GPU model retraining.
            - **Source Attribution**: RAG provides citations (document name, page number, exact snippet), virtually eliminating ungrounded hallucinations.
            - **Zero Data Leakage**: Proprietary college regulations and student marks remain in local storage rather than training public models.
            """
        )

    with st.expander("Q2: How does the Student Memory mechanism function?"):
        st.markdown(
            """
            Student details (Department, Semester, Subjects, Target GPA) are stored persistently in **SQLite**.
            When a query is dispatched, the `StudentMemory` module compiles this profile into a system instruction block,
            informing Gemini of the student's background so queries like *"What subjects should I prioritize?"* are automatically answered
            for their specific semester and courses without repetitive prompting.
            """
        )

    with st.expander("Q3: How does the chunking and vector retrieval pipeline work?"):
        st.markdown(
            """
            1. **PDF Extraction**: `PDFDocumentLoader` parses each page, attaching metadata (`source`, `page`).
            2. **Chunking**: `RecursiveCharacterTextSplitter` chunks pages into 750-character segments with 120-character overlap to retain continuity across sentence boundaries.
            3. **Embedding**: `GoogleGenerativeAIEmbeddings` generates vectors for each chunk.
            4. **Vector Storage**: Stored in persistent `ChromaDB` using cosine similarity search.
            """
        )

    st.markdown("---")
    st.caption("CampusAI • Final Year Project • Built with Streamlit, LangChain, Google Gemini, ChromaDB & SQLite")
