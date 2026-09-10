"""
AI Study Planner Page for CampusAI.
Generates personalized exam study schedules, priority matrices, and revision plans.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from memory.student_memory import StudentMemory
from tools.study_planner import StudyPlannerTool
from database.sqlite_db import get_recent_study_plans
from utils.helpers import setup_page


def main():
    setup_page(
        title="AI Study Planner",
        subtitle="Generate intelligent revision roadmaps, subject priority matrices, and daily timetables",
        icon="📅"
    )

    profile = StudentMemory.get_profile()

    tab_create, tab_saved = st.tabs(["✨ Generate New Study Plan", "📂 View Saved Plans"])

    with tab_create:
        st.markdown("### 📋 Study Plan Parameters")

        with st.form("study_plan_form"):
            col1, col2 = st.columns(2)

            with col1:
                default_exam_date = date.today() + timedelta(days=21)
                exam_date = st.date_input(
                    "Target Exam Date",
                    value=default_exam_date,
                    min_value=date.today(),
                    help="The date when your first or major examination commences"
                )

                daily_hours = st.slider(
                    "Hours Available Per Day",
                    min_value=1.0,
                    max_value=12.0,
                    value=4.5,
                    step=0.5,
                    help="Dedicated daily study and revision hours"
                )

                specific_goals = st.text_input(
                    "Target Goals or Weak Areas",
                    placeholder="e.g., Focus heavily on Compiler Design parsing and AI search algorithms",
                    help="Optional specific focus instructions"
                )

            with col2:
                st.write("**Enrolled Subjects (From Profile)**")
                default_subjects = profile.subjects
                selected_subjects = st.multiselect(
                    "Select Subjects to Include in Schedule",
                    options=default_subjects + ["Custom Subject 1", "Custom Subject 2"],
                    default=default_subjects,
                    help="Customize subjects to study for this exam period"
                )

                st.write("**Subject Difficulty Breakdown**")
                difficulty_map = {}
                for subj in selected_subjects[:4]:  # Limit UI clutter
                    difficulty_map[subj] = st.select_slider(
                        f"Difficulty: {subj}",
                        options=["Easy", "Medium", "Hard"],
                        value="Medium",
                        key=f"diff_{subj}"
                    )

            submitted = st.form_submit_button("🚀 Generate Personalized Study Plan", use_container_width=True)

        if submitted:
            if not selected_subjects:
                st.error("Please select at least one subject to generate a study plan.")
            else:
                with st.spinner("AI Study Coach is designing your personalized timetable..."):
                    result = StudyPlannerTool.generate_plan(
                        exam_date=str(exam_date),
                        subjects=selected_subjects,
                        daily_hours=daily_hours,
                        difficulty_levels=difficulty_map,
                        specific_goals=specific_goals
                    )

                    if result["success"]:
                        st.session_state["current_study_plan"] = result["plan_markdown"]
                        st.session_state["plan_days_left"] = result["days_left"]
                        st.success(f"🎉 Study Plan created successfully! {result['days_left']} days remaining until exam.")
                    else:
                        st.error(f"Error: {result.get('error', 'Failed generating plan.')}")

        # Display currently generated plan if available
        if "current_study_plan" in st.session_state:
            st.markdown("---")
            st.markdown("### 🗓️ Your Personalized AI Study Timetable")

            days_left = st.session_state.get("plan_days_left", "")
            st.info(f"⏳ **Countdown:** {days_left} Days remaining. Stick to your daily blocks for maximum retention!")

            st.markdown(st.session_state["current_study_plan"])

            # Download Plan
            st.download_button(
                label="📥 Download Study Plan (.md)",
                data=st.session_state["current_study_plan"],
                file_name=f"CampusAI_StudyPlan_{date.today()}.md",
                mime="text/markdown",
                use_container_width=True
            )

    with tab_saved:
        st.markdown("### 🗄️ Past Generated Study Plans")
        saved_plans = get_recent_study_plans(limit=10)

        if not saved_plans:
            st.info("No saved study plans found in SQLite database yet.")
        else:
            for plan in saved_plans:
                with st.expander(f"📌 Exam on {plan.exam_date} ({plan.daily_hours} hrs/day) — Created: {plan.created_at[:10]}"):
                    st.write(f"**Subjects:** {plan.subjects}")
                    st.markdown(plan.plan_content)
                    st.download_button(
                        label="📥 Download This Plan",
                        data=plan.plan_content,
                        file_name=f"StudyPlan_{plan.exam_date}.md",
                        key=f"dl_plan_{plan.id}"
                    )


main()
