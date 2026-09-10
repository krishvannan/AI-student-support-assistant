"""
Student Memory Module for CampusAI.
Retrieves student profile from SQLite and formats dynamic personalization contexts for AI prompts.
"""

from typing import Optional
from database.sqlite_db import get_student_profile
from database.models import StudentProfile


class StudentMemory:
    """Manages student context and memory injection for AI prompts."""

    @staticmethod
    def get_profile() -> StudentProfile:
        """Fetch current student profile from SQLite database."""
        return get_student_profile()

    @classmethod
    def get_context_prompt(cls) -> str:
        """
        Generate a formatted system context prompt incorporating the student's profile.
        This provides persona and background to Gemini for personalized responses.
        """
        profile = cls.get_profile()

        subjects_str = profile.subjects_as_string()
        prompt = (
            f"--- ACTIVE STUDENT PROFILE ---\n"
            f"Student Name: {profile.name}\n"
            f"Department: {profile.department}\n"
            f"Current Semester: Semester {profile.semester}\n"
            f"Enrolled Subjects: {subjects_str}\n"
            f"Target CGPA/GPA: {profile.target_gpa}\n"
            f"Preferred Language: {profile.preferred_language}\n"
            f"Academic Interests/Goals: {profile.interests}\n"
            f"--------------------------------\n"
            f"Instructions for AI:\n"
            f"1. Remember and leverage this student's identity when answering.\n"
            f"2. When the student asks questions like 'What subjects should I prioritize?' or 'Help me prepare for my exams', "
            f"directly refer to their specific enrolled subjects ({subjects_str}) and department ({profile.department}).\n"
            f"3. Tailor tone, complexity, and examples to a Semester {profile.semester} university student.\n"
            f"4. If the preferred language is not English, you may provide greetings or answers in their preferred language ({profile.preferred_language}) where appropriate or requested.\n"
        )
        return prompt

    @classmethod
    def get_short_summary(cls) -> str:
        """Return a single-line summary of the active student for badges/headers."""
        profile = cls.get_profile()
        return f"{profile.name} | {profile.department} (Sem {profile.semester}) | Target GPA: {profile.target_gpa}"
