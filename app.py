"""
CampusAI – Intelligent Student Support Assistant
Main Streamlit Application Entrypoint.

Tech Stack:
- Frontend: Streamlit
- AI Framework: LangChain
- LLM: Google Gemini
- Embeddings: Gemini Embeddings
- Vector DB: ChromaDB
- Relational DB: SQLite
- Document Processing: PyPDF2 / pypdf
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from utils.config import ensure_directories, is_api_key_set
from utils.helpers import load_css, render_api_key_sidebar
from database.sqlite_db import init_db
from memory.student_memory import StudentMemory

# Import Page Renderers
from pages.home import render_home_page
from pages.chatbot import render_chatbot_page
from pages.study_planner import render_study_planner_page
from pages.quiz_generator import render_quiz_page
from pages.summarizer import render_summarizer_page
from pages.profile import render_profile_page
from pages.about import render_about_page

# Page Configuration
st.set_page_config(
    page_title="CampusAI – Student Support Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main application lifecycle and page routing."""
    # Ensure system directories and SQLite tables exist
    ensure_directories()
    init_db()
    load_css()

    # Sidebar Branding
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 0.5rem;">
            <div style="font-size: 2.2rem;">🏛️</div>
            <h2 style="margin: 0; color: #1e40af; font-weight: 800; font-size: 1.4rem;">CampusAI</h2>
            <p style="margin: 0; color: #64748b; font-size: 0.8rem; font-weight: 500;">Intelligent Student Support Assistant</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Active Student Snapshot in Sidebar
    profile = StudentMemory.get_profile()
    st.sidebar.markdown(
        f"""
        <div style="background: #f1f5f9; border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 1.2rem; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.75rem; text-transform: uppercase; color: #64748b; font-weight: 700;">Active Student</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a;">{profile.name}</div>
            <div style="font-size: 0.8rem; color: #475569;">Sem {profile.semester} • {profile.department[:18]}...</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Navigation Menu
    nav_options = [
        "🏠 Home",
        "💬 Ask College Assistant",
        "📅 Study Planner",
        "📝 Quiz Generator",
        "📄 Notice Summarizer",
        "👤 Student Profile",
        "ℹ About"
    ]

    # Handle external page routing from buttons
    default_idx = 0
    if "nav_page" in st.session_state and st.session_state["nav_page"] in nav_options:
        default_idx = nav_options.index(st.session_state["nav_page"])

    selected_page = st.sidebar.radio(
        "Navigation Menu",
        options=nav_options,
        index=default_idx,
        key="nav_radio"
    )

    # Reset explicit navigation state so sidebar remains in sync
    st.session_state["nav_page"] = selected_page

    # Render API Key input / status widget in sidebar
    render_api_key_sidebar()

    # Sidebar Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("🚀 **CampusAI v1.0.0**\nPowered by Google Gemini & LangChain")

    # API Key warning banner if not set
    if not is_api_key_set():
        st.sidebar.info("💡 **Quick Setup**: Enter your Google Gemini API key above or in `.env` to activate AI generation.")

    # Page Routing
    if selected_page == "🏠 Home":
        render_home_page()
    elif selected_page == "💬 Ask College Assistant":
        render_chatbot_page()
    elif selected_page == "📅 Study Planner":
        render_study_planner_page()
    elif selected_page == "📝 Quiz Generator":
        render_quiz_page()
    elif selected_page == "📄 Notice Summarizer":
        render_summarizer_page()
    elif selected_page == "👤 Student Profile":
        render_profile_page()
    elif selected_page == "ℹ About":
        render_about_page()


if __name__ == "__main__":
    main()
