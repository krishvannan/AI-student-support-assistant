"""
UI and Utility Helpers for CampusAI Streamlit App.
Provides custom styling injection, header components, shared sidebars, and state management.
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.config import ASSETS_DIR, is_api_key_set, set_api_key, get_api_key, ensure_directories
from database.sqlite_db import init_db
from memory.student_memory import StudentMemory


def load_css() -> None:
    """Inject custom CSS into Streamlit application."""
    css_file = ASSETS_DIR / "style.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_header(title: str, subtitle: str, icon: str = "🎓") -> None:
    """Render a consistent header banner with university styling."""
    profile = StudentMemory.get_profile()
    dept_short = profile.department if len(profile.department) <= 24 else profile.department[:22] + "..."
    st.markdown(
        f"""
        <div class="campus-header">
            <div class="header-main">
                <h1>{icon} {title}</h1>
                <p>{subtitle}</p>
            </div>
            <div class="header-student-card">
                <div class="header-student-name">{profile.name}</div>
                <div class="header-student-meta">{dept_short} • Sem {profile.semester}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_shared_sidebar() -> None:
    """Render shared sidebar branding, student snapshot, and API key management."""
    # Branding
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 0.4rem 0 0.9rem 0;">
            <div style="font-size: 2.1rem; line-height: 1;">🏛️</div>
            <h2 style="margin: 0.2rem 0 0 0; color: #1e40af; font-weight: 700; font-size: 1.35rem; letter-spacing: -0.02em;">CampusAI</h2>
            <p style="margin: 0.1rem 0 0 0; color: #64748b; font-size: 0.82rem; font-weight: 500;">Student Support Assistant</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Student Profile Snapshot
    profile = StudentMemory.get_profile()
    dept_short = profile.department if len(profile.department) <= 24 else profile.department[:22] + "..."
    st.sidebar.markdown(
        f"""
        <div style="background: #ffffff; border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 1.1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);">
            <div style="font-size: 0.72rem; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.05em;">Active Student</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-top: 0.1rem;">{profile.name}</div>
            <div style="font-size: 0.8rem; color: #475569;">Sem {profile.semester} • {dept_short}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # API Key Configuration Widget
    render_api_key_sidebar()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("🚀 **CampusAI v1.0.0**\nPowered by Google Gemini & LangChain")


def render_api_key_sidebar() -> None:
    """Sidebar widget to view/update Google Gemini API key dynamically."""
    st.sidebar.subheader("🔑 AI Configuration")

    current_key = get_api_key()
    has_key = is_api_key_set()

    if has_key:
        masked_key = current_key[:4] + "••••••••" + current_key[-4:] if len(current_key) > 8 else "••••••••"
        st.sidebar.success("✅ Gemini API Key Active")
        with st.sidebar.expander("Update API Key"):
            new_key = st.text_input("Enter New Key", type="password", key="new_api_key_input")
            if st.button("Update Key", key="btn_update_key"):
                if new_key.strip():
                    set_api_key(new_key.strip())
                    st.success("API Key updated successfully!")
                    st.rerun()
    else:
        st.sidebar.warning("⚠️ API Key Not Configured")
        key_input = st.sidebar.text_input(
            "Gemini API Key",
            type="password",
            placeholder="Paste AI Studio key...",
            help="Get free key at aistudio.google.com"
        )
        if st.sidebar.button("Save API Key", key="btn_save_key"):
            if key_input.strip():
                set_api_key(key_input.strip())
                st.sidebar.success("Key saved!")
                st.rerun()


def setup_page(title: str, subtitle: str, icon: str = "🎓") -> None:
    """Common setup routine for each page."""
    ensure_directories()
    init_db()
    load_css()
    render_shared_sidebar()
    render_header(title, subtitle, icon)


def extract_text_from_response(content) -> str:
    """
    Extract clean string from LangChain Gemini response content,
    which may be a string or list of content dictionaries.
    """
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "\n".join(parts).strip()
    return str(content).strip()

