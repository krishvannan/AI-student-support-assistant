"""CampusAI Database package."""
from database.sqlite_db import (
    init_db,
    get_student_profile,
    save_or_update_profile,
    save_study_plan,
    get_recent_study_plans,
    add_chat_message,
    get_chat_history,
    clear_chat_history,
    save_quiz_record,
    get_recent_quizzes,
)
from database.models import StudentProfile, StudyPlan, ChatMessage, QuizRecord

__all__ = [
    "init_db",
    "get_student_profile",
    "save_or_update_profile",
    "save_study_plan",
    "get_recent_study_plans",
    "add_chat_message",
    "get_chat_history",
    "clear_chat_history",
    "save_quiz_record",
    "get_recent_quizzes",
    "StudentProfile",
    "StudyPlan",
    "ChatMessage",
    "QuizRecord",
]
