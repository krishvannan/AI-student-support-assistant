"""
UI and Utility Helpers for CampusAI Streamlit App.
Provides custom styling injection, header components, and state checks.
"""

import streamlit as st
from utils.config import ASSETS_DIR, is_api_key_set, set_api_key, get_api_key
from memory.student_memory import StudentMemory


def load_css() -> None:
    """Inject custom CSS into Streamlit application."""
    css_file = ASSETS_DIR / "style.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_header(title: str, subtitle: str, icon: str = "🎓") -> None:
    """Render a header banner with university styling."""
    profile = StudentMemory.get_profile()
    st.markdown(
        f"""
        <div class="campus-header">
            <div>
                <h1>{icon} {title}</h1>
                <p>{subtitle}</p>
            </div>
            <div style="text-align: right; font-size: 0.9rem; background: rgba(255,255,255,0.12); padding: 0.6rem 1.2rem; border-radius: 12px; backdrop-filter: blur(4px);">
                <div style="font-weight: 700; color: #f8fafc;">{profile.name}</div>
                <div style="color: #93c5fd; font-size: 0.82rem;">{profile.department} • Sem {profile.semester}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_api_key_sidebar() -> None:
    """Sidebar widget to view/update Google Gemini API key dynamically."""
    st.sidebar.markdown("---")
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
