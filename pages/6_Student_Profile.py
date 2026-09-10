"""
Student Profile Page for CampusAI.
Manages student information stored in SQLite, which drives conversational memory and personalized AI tools.
"""

import sys
from pathlib import Path
from typing import List
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from memory.student_memory import StudentMemory
from database.sqlite_db import save_or_update_profile
from database.models import StudentProfile
from utils.helpers import setup_page


def main():
    setup_page(
        title="Student Profile & Memory",
        subtitle="Manage your academic records, enrolled subjects, and language preferences stored in SQLite",
        icon="👤"
    )

    profile = StudentMemory.get_profile()

    col_form, col_preview = st.columns([1.2, 1])

    with col_form:
        st.markdown("### ✏️ Edit Academic Profile")

        with st.form("student_profile_form"):
            name = st.text_input("Full Name", value=profile.name)
            roll_number = st.text_input("Roll / Register Number", value=profile.roll_number, placeholder="e.g., 2021CS1042")

            c_dept, c_sem = st.columns([2, 1])
            with c_dept:
                departments = [
                    "Computer Science and Engineering",
                    "Artificial Intelligence and Data Science",
                    "Information Technology",
                    "Electronics and Communication Engineering",
                    "Electrical and Electronics Engineering",
                    "Mechanical Engineering",
                    "Civil Engineering"
                ]
                dept_index = departments.index(profile.department) if profile.department in departments else 0
                department = st.selectbox("Department / Branch", departments, index=dept_index)

            with c_sem:
                semester = st.selectbox("Current Semester", list(range(1, 9)), index=max(0, min(7, profile.semester - 1)))

            # Subjects as comma-separated string
            subjects_text = st.text_area(
                "Enrolled Subjects (comma-separated)",
                value=profile.subjects_as_string(),
                help="List courses enrolled in this semester. AI will prioritize and personalize based on these!"
            )

            c_gpa, c_lang = st.columns(2)
            with c_gpa:
                target_gpa = st.slider("Target CGPA / GPA", min_value=5.0, max_value=10.0, value=float(profile.target_gpa), step=0.1)

            with c_lang:
                languages = ["English", "Tamil", "Hindi", "Telugu", "Malayalam", "Spanish", "French"]
                lang_idx = languages.index(profile.preferred_language) if profile.preferred_language in languages else 0
                preferred_language = st.selectbox("Preferred AI Language", languages, index=lang_idx)

            interests = st.text_input("Academic Goals / Areas of Interest", value=profile.interests)

            save_submitted = st.form_submit_button("💾 Save Profile to SQLite", use_container_width=True)

        if save_submitted:
            cleaned_subjects = [s.strip() for s in subjects_text.split(",") if s.strip()]
            updated_profile = StudentProfile(
                id=profile.id,
                name=name.strip() or "Student",
                roll_number=roll_number.strip(),
                department=department,
                semester=semester,
                subjects=cleaned_subjects,
                target_gpa=target_gpa,
                preferred_language=preferred_language,
                interests=interests.strip()
            )

            save_or_update_profile(updated_profile)
            st.success("✅ Profile successfully updated in SQLite! Conversational memory is now synchronized.")
            st.rerun()

    with col_preview:
        st.markdown("### 🧠 Live Conversational Memory Preview")
        st.caption("This context is injected into every Gemini prompt to give the AI memory of who you are.")

        memory_prompt = StudentMemory.get_context_prompt()
        st.code(memory_prompt, language="markdown")

        st.markdown("---")
        st.markdown("#### 🔍 How Memory Personalization Works")
        st.markdown(
            """
            1. **Persistent SQLite Store**: Your profile is stored in the local SQLite database.
            2. **Dynamic Prompt Augmentation**: Every user prompt in the **College Assistant**, **Study Planner**, and **Quiz Generator** automatically loads your active semester, department, and subjects.
            3. **Multi-Turn Continuity**: When you ask *"What subjects should I prepare for?"*, the assistant knows you are in *Semester %s of %s* without having to re-ask.
            """ % (profile.semester, profile.department)
        )


if __name__ == "__main__" or True:
    main()
