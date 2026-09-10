"""
CampusAI – Intelligent Student Support Assistant
Official Streamlit Multipage Application Entrypoint.

Tech Stack:
- Frontend: Streamlit Multipage Architecture
- AI Framework: LangChain
- LLM: Google Gemini
- Embeddings: Gemini Embeddings
- Vector DB: ChromaDB
- Relational DB: SQLite
- Document Processing: PyPDF2 / pypdf
"""

import sys
from pathlib import Path
import streamlit as st

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.sqlite_db import init_db
from utils.config import ensure_directories

# Configure Streamlit page settings (must be the first Streamlit command)
st.set_page_config(
    page_title="CampusAI – Student Support Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and system directories
ensure_directories()
init_db()

# Define Official Streamlit Multipage Navigation
home_page = st.Page("pages/1_Home.py", title="Home", icon="🏠", default=True)
assistant_page = st.Page("pages/2_College_Assistant.py", title="College Assistant", icon="💬")
planner_page = st.Page("pages/3_Study_Planner.py", title="Study Planner", icon="📅")
quiz_page = st.Page("pages/4_Quiz_Generator.py", title="Quiz Generator", icon="📝")
summarizer_page = st.Page("pages/5_Notice_Summarizer.py", title="Notice Summarizer", icon="📄")
profile_page = st.Page("pages/6_Student_Profile.py", title="Student Profile", icon="👤")
about_page = st.Page("pages/7_About.py", title="About", icon="ℹ️")

# Build navigation structure
pg = st.navigation(
    [
        home_page,
        assistant_page,
        planner_page,
        quiz_page,
        summarizer_page,
        profile_page,
        about_page
    ]
)

# Run the active page
pg.run()
