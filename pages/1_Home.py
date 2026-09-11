"""
Home Page for CampusAI.
Displays the university student dashboard, active profile snapshot, quick stats, and navigation cards.
"""

import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from memory.student_memory import StudentMemory
from rag.vectorstore import get_vector_store
from database.sqlite_db import get_recent_study_plans, get_recent_quizzes
from utils.helpers import setup_page


def main():
    setup_page(
        title="CampusAI Student Dashboard",
        subtitle="Your personalized AI assistant for academic regulations, study planning, circulars, and exam prep",
        icon="🏛️"
    )

    profile = StudentMemory.get_profile()
    vector_store = get_vector_store()
    doc_count = vector_store.get_document_count()
    indexed_files = vector_store.get_indexed_files()

    # Student Overview Card & Quick Stats
    st.markdown("### 👤 Active Student Snapshot")
    col_profile, col_stats1, col_stats2, col_stats3 = st.columns([2, 1, 1, 1])

    with col_profile:
        st.markdown(
            f"""
            <div class="student-snapshot-card" style="border-left: 4px solid #1e40af;">
                <div style="font-size: 1.15rem; font-weight: 700; color: #1e40af;">{profile.name}</div>
                <div style="font-size: 0.9rem; color: #475569; margin-top: 0.2rem;">
                    🎓 <b>{profile.department}</b> • Semester {profile.semester}
                </div>
                <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.4rem;">
                    📚 Enrolled: <i>{profile.subjects_as_string()}</i>
                </div>
                <div style="margin-top: 0.6rem;">
                    <span class="student-status-badge">🎯 Target GPA: {profile.target_gpa}</span>
                    <span class="student-status-badge" style="background:#eff6ff; border-color:#bfdbfe; color:#1e40af;">
                        🌐 {profile.preferred_language}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    recent_plans = get_recent_study_plans(limit=5)
    recent_quizzes = get_recent_quizzes(limit=5)

    with col_stats1:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-number">{len(profile.subjects)}</div>
                <div class="stat-label">Subjects</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_stats2:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-number">{doc_count}</div>
                <div class="stat-label">Indexed Chunks</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_stats3:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-number">{len(recent_quizzes)}</div>
                <div class="stat-label">Quizzes Taken</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Core Features Navigation Grid
    st.markdown("### ⚡ AI Core Features")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-badge">💬</div>
                <h3>Ask Assistant</h3>
                <p>Query university regulations, grading rules, syllabus, and exams with instant citations.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Assistant →", key="btn_nav_assistant", use_container_width=True):
            st.switch_page("pages/2_College_Assistant.py")

    with c2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-badge">📅</div>
                <h3>Study Planner</h3>
                <p>Generate science-backed revision roadmaps, daily study schedules, and priority matrices.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Create Plan →", key="btn_nav_planner", use_container_width=True):
            st.switch_page("pages/3_Study_Planner.py")

    with c3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-badge">📝</div>
                <h3>Quiz Generator</h3>
                <p>Create test-standard multiple-choice questions from lecture notes or syllabus topics.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Generate Quiz →", key="btn_nav_quiz", use_container_width=True):
            st.switch_page("pages/4_Quiz_Generator.py")

    with c4:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-badge">📄</div>
                <h3>Notice Summarizer</h3>
                <p>Convert long college circulars into executive summaries, deadline alerts, and action items.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Summarize Notice →", key="btn_nav_sum", use_container_width=True):
            st.switch_page("pages/5_Notice_Summarizer.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # Document Repository Status & Recent Activity
    col_docs, col_recent = st.columns([1, 1])

    with col_docs:
        st.markdown("### 📂 Indexed Knowledge Repository")
        if indexed_files:
            st.success(f"🗃️ **{len(indexed_files)} Documents indexed in ChromaDB vector store:**")
            for f in indexed_files:
                st.markdown(f"- 📄 `{f}`")
        else:
            st.info("No documents are currently indexed in ChromaDB. Go to **Ask College Assistant** to upload or index sample PDFs.")

    with col_recent:
        st.markdown("### 🕒 Recent Activity")
        if recent_plans:
            latest_plan = recent_plans[0]
            st.markdown(f"**Latest Study Plan:** Exam on `{latest_plan.exam_date}` ({latest_plan.daily_hours} hrs/day)")
        if recent_quizzes:
            latest_quiz = recent_quizzes[0]
            st.markdown(f"**Latest Quiz:** `{latest_quiz.topic}` - Score: **{latest_quiz.score}/{latest_quiz.total_questions}**")
        if not recent_plans and not recent_quizzes:
            st.markdown("No recent activities recorded. Start exploring with the assistant above!")


main()
