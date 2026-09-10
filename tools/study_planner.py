"""
AI Study Planner Tool for CampusAI.
Generates structured revision timetables, subject priority matrices, and daily schedules using Google Gemini.
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional
from utils.config import get_api_key, GEMINI_MODEL, is_api_key_set
from memory.student_memory import StudentMemory
from database.sqlite_db import save_study_plan
from database.models import StudyPlan

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage


class StudyPlannerTool:
    """Generates structured study plans tailored to student exams and schedules."""

    @staticmethod
    def generate_plan(
        exam_date: str,
        subjects: List[str],
        daily_hours: float = 4.0,
        difficulty_levels: Optional[Dict[str, str]] = None,
        specific_goals: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive study plan using Gemini.
        Returns dictionary with markdown content and metadata.
        """
        if not is_api_key_set():
            return {
                "success": False,
                "error": "Google Gemini API Key is not set. Please add it in Settings.",
                "plan_markdown": ""
            }

        api_key = get_api_key()
        student_profile = StudentMemory.get_profile()

        # Calculate days until exam
        try:
            today = date.today()
            exam_d = datetime.strptime(exam_date, "%Y-%m-%d").date()
            days_left = (exam_d - today).days
            if days_left < 1:
                days_left = 1
        except Exception:
            days_left = 14

        diff_summary = ""
        if difficulty_levels:
            diff_summary = "Subject Difficulty Breakdown:\n" + "\n".join(
                [f"- {subj}: {level}" for subj, level in difficulty_levels.items()]
            )

        system_prompt = (
            "You are an expert Academic Advisor and Cognitive Study Coach at a top engineering university.\n"
            "Your task is to design a realistic, high-impact, science-backed study schedule for a college student.\n"
            "Apply cognitive science techniques: spaced repetition, active recall, Pomodoro intervals, and interleaved practice.\n\n"
            f"{StudentMemory.get_context_prompt()}\n"
        )

        user_prompt = (
            f"Please generate a comprehensive study plan with the following constraints:\n"
            f"- Exam Date: {exam_date} ({days_left} days remaining)\n"
            f"- Daily Study Time: {daily_hours} hours/day\n"
            f"- Subjects Enrolled: {', '.join(subjects)}\n"
            f"{diff_summary}\n"
            f"- Specific Goals / Focus Areas: {specific_goals if specific_goals else 'Balanced preparation'}\n\n"
            "Structure your output in clear Markdown with the following exact sections:\n\n"
            "1. 🎯 **Executive Strategy & Subject Priority Matrix**\n"
            "Provide a table categorizing each subject by priority (High / Medium / Light) and hours allocated per week.\n\n"
            "2. 📅 **Daily Study Routine & Timetable (Structured Table)**\n"
            "Provide a markdown table showing the daily hourly study routine:\n"
            "| Time Block | Duration | Focus Area | Subject | Activity / Pomodoro Interval |\n\n"
            "3. 🗓️ **Milestone & Day-by-Day Revision Schedule (Structured Table)**\n"
            "Provide a day-by-day or phase-by-phase schedule in a clean markdown table:\n"
            "| Phase / Days | Primary Subject | High-Yield Topics Covered | Practice & Problem Sets | Revision Checkpoint |\n\n"
            "4. 🔄 **Spaced Repetition Checkpoints**\n"
            "Guidelines on when and how to review past topics.\n\n"
            "5. 💡 **High-Yield Exam Preparation Tips**\n"
            "Actionable tips tailored specifically to engineering exams.\n"
        )

        try:
            llm = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=api_key,
                temperature=0.3
            )
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            plan_content = response.content
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed generating study plan: {str(e)}",
                "plan_markdown": ""
            }

        # Save to SQLite
        try:
            plan_record = StudyPlan(
                student_id=student_profile.id,
                exam_date=exam_date,
                daily_hours=daily_hours,
                subjects=", ".join(subjects),
                plan_content=plan_content,
                created_at=datetime.now().isoformat()
            )
            save_study_plan(plan_record)
        except Exception as e:
            print(f"Warning: Could not save study plan to SQLite: {e}")

        return {
            "success": True,
            "days_left": days_left,
            "plan_markdown": plan_content
        }
